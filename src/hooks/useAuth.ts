import { useState, useEffect } from 'react';
import { CognitoIdentityClient } from '@aws-sdk/client-cognito-identity';
import { fromCognitoIdentityPool } from '@aws-sdk/credential-provider-cognito-identity';
import { CognitoUser, AuthenticationDetails, CognitoUserPool } from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!,
  ClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,
};

const userPool = new CognitoUserPool(poolData);

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const cognitoUser = userPool.getCurrentUser();
      if (cognitoUser) {
        await new Promise((resolve, reject) => {
          cognitoUser.getSession((err: any, session: any) => {
            if (err) {
              reject(err);
              return;
            }
            if (session.isValid()) {
              setIsAuthenticated(true);
            } else {
              setIsAuthenticated(false);
            }
            resolve(session);
          });
        });
      }
    } catch (err) {
      console.error('Auth check error:', err);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const getCredentials = async () => {
    try {
      const cognitoUser = userPool.getCurrentUser();
      if (!cognitoUser) {
        throw new Error('No authenticated user');
      }

      return new Promise((resolve, reject) => {
        cognitoUser.getSession(async (err: any, session: any) => {
          if (err) {
            reject(err);
            return;
          }

          const loginKey = `cognito-idp.${process.env.NEXT_PUBLIC_COGNITO_USER_POOL_REGION}.amazonaws.com/${process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID}`;
          
          const credentialsProvider = fromCognitoIdentityPool({
            client: new CognitoIdentityClient({ 
              region: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_REGION 
            }),
            identityPoolId: process.env.NEXT_PUBLIC_COGNITO_IDENTITY_POOL_ID!,
            logins: {
              [loginKey]: session.getIdToken().getJwtToken()
            }
          });

          try {
            const credentials = await credentialsProvider();
            resolve(credentials);
          } catch (error) {
            reject(error);
          }
        });
      });
    } catch (error) {
      console.error('Error getting credentials:', error);
      throw error;
    }
  };

  const signIn = (username: string, password: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const authenticationDetails = new AuthenticationDetails({
        Username: username,
        Password: password,
      });

      const cognitoUser = new CognitoUser({
        Username: username,
        Pool: userPool,
      });

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: async (session) => {
          setIsAuthenticated(true);
          setError(null);
          resolve();
        },
        onFailure: (err) => {
          setError(err.message);
          reject(err);
        },
      });
    });
  };

  const signOut = () => {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
      setIsAuthenticated(false);
    }
  };

  return {
    isAuthenticated,
    isLoading,
    error,
    signIn,
    signOut,
    getCredentials,
  };
}