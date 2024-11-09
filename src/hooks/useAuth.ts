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
      } else {
        setIsAuthenticated(false);
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

          const region = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_REGION;
          const identityPoolId = process.env.NEXT_PUBLIC_COGNITO_IDENTITY_POOL_ID;
          const userPoolId = process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID;

          if (!region || !identityPoolId || !userPoolId) {
            reject(new Error('Missing required configuration'));
            return;
          }

          const loginKey = `cognito-idp.${region}.amazonaws.com/${userPoolId}`;
          
          try {
            const client = new CognitoIdentityClient({ region });
            const credentialsProvider = fromCognitoIdentityPool({
              client,
              identityPoolId,
              logins: {
                [loginKey]: session.getIdToken().getJwtToken()
              }
            });

            const credentials = await credentialsProvider();
            resolve(credentials);
          } catch (error) {
            console.error('Error getting credentials:', error);
            reject(error);
          }
        });
      });
    } catch (error) {
      console.error('Error in getCredentials:', error);
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
        newPasswordRequired: (userAttributes, requiredAttributes) => {
          reject(new Error('NEW_PASSWORD_REQUIRED'));
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