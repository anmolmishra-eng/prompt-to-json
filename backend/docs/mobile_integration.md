# Mobile Integration Guide

## Overview

The Design Engine API provides mobile-optimized endpoints for React Native/Expo applications. Mobile apps use the same JWT authentication and can call standard `/api/v1/` endpoints or mobile-specific wrappers.

## Authentication

Mobile apps use the same JWT authentication flow:

```javascript
// Login and get JWT token
const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch('https://api.designengine.com/api/v1/auth/login', {
    method: 'POST',
    body: formData,
  });
  
  const data = await response.json();
  return data.access_token;
};
```

## Mobile Endpoints

### Mobile-Specific Wrappers

Mobile apps can use dedicated endpoints with the same functionality:

- `POST /api/v1/mobile/generate` - Generate design specs
- `POST /api/v1/mobile/evaluate` - Rate designs  
- `POST /api/v1/mobile/iterate` - Improve designs
- `POST /api/v1/mobile/switch` - Change materials
- `GET /api/v1/mobile/health` - Mobile health check

### Standard API Usage

Mobile apps can also call standard endpoints directly:

```javascript
// Generate design spec
const generateDesign = async (token, prompt) => {
  const response = await fetch('https://api.designengine.com/api/v1/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: 'mobile_user_123',
      prompt: prompt,
      context: { platform: 'mobile' },
      project_id: 'mobile_project'
    }),
  });
  
  return await response.json();
};
```

## Expo Example

Complete React Native/Expo integration example:

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = 'https://api.designengine.com/api/v1';

export default function DesignApp() {
  const [token, setToken] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [design, setDesign] = useState(null);

  // Load saved token
  useEffect(() => {
    AsyncStorage.getItem('auth_token').then(setToken);
  }, []);

  // Login function
  const login = async () => {
    try {
      const formData = new FormData();
      formData.append('username', 'user');
      formData.append('password', 'pass');
      
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.access_token) {
        setToken(data.access_token);
        await AsyncStorage.setItem('auth_token', data.access_token);
        Alert.alert('Success', 'Logged in successfully');
      }
    } catch (error) {
      Alert.alert('Error', 'Login failed');
    }
  };

  // Generate design
  const generateDesign = async () => {
    if (!token || !prompt) return;
    
    try {
      const response = await fetch(`${API_BASE}/mobile/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'mobile_user',
          prompt: prompt,
          context: { 
            platform: 'mobile',
            device: 'smartphone' 
          },
          project_id: 'mobile_project'
        }),
      });
      
      const result = await response.json();
      setDesign(result);
      Alert.alert('Success', `Generated spec: ${result.spec_id}`);
    } catch (error) {
      Alert.alert('Error', 'Generation failed');
    }
  };

  // Evaluate design
  const evaluateDesign = async (rating) => {
    if (!token || !design) return;
    
    try {
      await fetch(`${API_BASE}/mobile/evaluate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          spec_id: design.spec_id,
          user_id: 'mobile_user',
          rating: rating,
          notes: 'Mobile app evaluation'
        }),
      });
      
      Alert.alert('Success', 'Design rated successfully');
    } catch (error) {
      Alert.alert('Error', 'Rating failed');
    }
  };

  return (
    <View style={{ padding: 20 }}>
      {!token ? (
        <Button title="Login" onPress={login} />
      ) : (
        <>
          <TextInput
            placeholder="Enter design prompt"
            value={prompt}
            onChangeText={setPrompt}
            style={{ borderWidth: 1, padding: 10, marginBottom: 10 }}
          />
          
          <Button title="Generate Design" onPress={generateDesign} />
          
          {design && (
            <View style={{ marginTop: 20 }}>
              <Text>Spec ID: {design.spec_id}</Text>
              <Text>Preview: {design.preview_url}</Text>
              
              <View style={{ flexDirection: 'row', marginTop: 10 }}>
                <Button title="Rate 1⭐" onPress={() => evaluateDesign(1)} />
                <Button title="Rate 5⭐" onPress={() => evaluateDesign(5)} />
              </View>
            </View>
          )}
        </>
      )}
    </View>
  );
}
```

## Mobile-Specific Features

### Optimized Responses

Mobile endpoints return optimized data structures:

```javascript
// Mobile health check includes platform info
{
  "status": "ok",
  "platform": "mobile",
  "api_version": "v1"
}
```

### Error Handling

```javascript
const handleApiCall = async (apiCall) => {
  try {
    const response = await apiCall();
    
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, redirect to login
        await AsyncStorage.removeItem('auth_token');
        setToken(null);
      }
      throw new Error(`API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    Alert.alert('Error', error.message);
    throw error;
  }
};
```

### Offline Support

```javascript
import NetInfo from '@react-native-netinfo/netinfo';

const checkConnectivity = async () => {
  const netInfo = await NetInfo.fetch();
  
  if (!netInfo.isConnected) {
    Alert.alert('Offline', 'Please check your internet connection');
    return false;
  }
  
  return true;
};
```

## Installation

Add required dependencies to your Expo/React Native project:

```bash
npm install @react-native-async-storage/async-storage
npm install @react-native-netinfo/netinfo
```

## Best Practices

1. **Token Management:** Store JWT tokens securely using AsyncStorage
2. **Error Handling:** Implement proper error handling for network failures
3. **Offline Support:** Cache critical data for offline usage
4. **Performance:** Use mobile-specific endpoints for optimized responses
5. **Security:** Always use HTTPS in production
6. **User Experience:** Provide loading states and error feedback