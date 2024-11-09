"use client"
import React from 'react';
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { CognitoUser, AuthenticationDetails, CognitoUserPool } from 'amazon-cognito-identity-js';

const poolData = {
  UserPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID!,
  ClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID!,
};

const userPool = new CognitoUserPool(poolData);

const AuthWrapper = ({ children }) => {
  const { isAuthenticated, isLoading, signIn } = useAuth();
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [loginLoading, setLoginLoading] = React.useState(false);
  const [requiresNewPassword, setRequiresNewPassword] = React.useState(false);
  const [error, setError] = React.useState("");
  const [cognitoUser, setCognitoUser] = React.useState<any>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setError("");

    const authenticationDetails = new AuthenticationDetails({
      Username: username,
      Password: password,
    });

    const userData = {
      Username: username,
      Pool: userPool,
    };

    const cognitoUserInstance = new CognitoUser(userData);

    cognitoUserInstance.authenticateUser(authenticationDetails, {
      onSuccess: () => {
        setLoginLoading(false);
        signIn(username, password);
      },
      onFailure: (err) => {
        console.error("Authentication error:", err);
        setError(err.message);
        setLoginLoading(false);
      },
      newPasswordRequired: () => {
        setRequiresNewPassword(true);
        setCognitoUser(cognitoUserInstance);
        setLoginLoading(false);
      },
    });
  };

  const handleNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      setLoginLoading(false);
      return;
    }

    // Create an empty userAttributes object - this is key to fixing the email error
    const userAttributes = {};

    try {
      cognitoUser.completeNewPasswordChallenge(
        newPassword,
        userAttributes,
        {
          onSuccess: async (session) => {
            try {
              await signIn(username, newPassword);
              setRequiresNewPassword(false);
              setCognitoUser(null);
            } catch (err) {
              setError("Failed to sign in with new password");
              console.error("Sign in error:", err);
            }
            setLoginLoading(false);
          },
          onFailure: (err) => {
            console.error("Password change error:", err);
            setError(err.message || "Failed to update password");
            setLoginLoading(false);
          },
        }
      );
    } catch (err: any) {
      console.error("Password change error:", err);
      setError(err.message || "Failed to update password");
      setLoginLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>
              {requiresNewPassword ? "Change Password" : "Sign In"}
            </CardTitle>
            {requiresNewPassword && (
              <CardDescription>
                Your temporary password has expired. Please set a new password to continue.
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            {!requiresNewPassword ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                {error && (
                  <p className="text-sm text-red-500">{error}</p>
                )}
                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={loginLoading}
                >
                  {loginLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Sign In
                </Button>
              </form>
            ) : (
              <form onSubmit={handleNewPassword} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Password must be at least 8 characters long and contain 
                    uppercase, lowercase, numbers and special characters
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>
                {error && (
                  <p className="text-sm text-red-500">{error}</p>
                )}
                <Button 
                  type="submit" 
                  className="w-full"
                  disabled={loginLoading}
                >
                  {loginLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Change Password
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return children;
};

export default AuthWrapper;