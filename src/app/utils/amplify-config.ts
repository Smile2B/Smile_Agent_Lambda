// src/app/utils/amplify-config.ts
import { type ResourcesConfig } from 'aws-amplify/config';

export const config: ResourcesConfig = {
  Auth: {
    Cognito: {
      userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID || 'your-user-pool-id',
      userPoolClientId: '5qg100paeghsi2csedccn9t17i',
      signUpVerificationMethod: 'code',
      loginWith: {
        email: true,
        username: true,
        phone: false
      },
      region: 'us-east-1'
    }
  },
  API: {
    REST: {
      WellArchitectAPI: {
        endpoint: process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'your-api-endpoint',
        region: 'us-east-1'
      }
    }
  }
};