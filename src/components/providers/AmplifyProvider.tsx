// src/components/providers/AmplifyProvider.tsx
"use client";

import { ReactNode } from 'react';
import { Amplify } from 'aws-amplify';

const config = {
  Auth: {
    Cognito: {
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID,
      userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID,
      signUpVerificationMethod: 'code',
      region: process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1'
    }
  },
  API: {
    REST: {
      WellArchitectAPI: {
        endpoint: process.env.NEXT_PUBLIC_API_GATEWAY_URL,
        region: process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1'
      }
    }
  }
};

Amplify.configure(config, { ssr: true });

interface AmplifyProviderProps {
  children: ReactNode;
}

export function AmplifyProvider({ children }: AmplifyProviderProps) {
  return children;
}