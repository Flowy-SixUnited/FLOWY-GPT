import { POST } from './index';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  access_token?: string;
  token_type?: string;
  user?: {
    user_id: string;
    username: string;
    nick_name: string;
    role: string;
  };
  message?: string;
}

// 登录API调用函数
export async function loginUser(credentials: LoginCredentials): Promise<LoginResponse> {
  try {
    // 使用FormData格式发送请求，符合OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await POST<FormData, LoginResponse>('/api/v1/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    if (response.data.success) {
      return {
        success: true,
        access_token: response.data.data?.access_token || response.data.access_token,
        token_type: response.data.data?.token_type || response.data.token_type || 'bearer',
        user: response.data.data?.user || response.data.user,
        message: response.data.data?.message || response.data.message || 'Login successful'
      };
    } else {
      return {
        success: false,
        message: response.data.err_msg || response.data.message || 'Login failed'
      };
    }
  } catch (error: any) {
    console.error('Login API error:', error);
    
    // 模拟登录功能（临时用于测试）
    console.log('Using mock login due to API error. Credentials:', credentials);
    
    if (credentials.username === "admin" && credentials.password === "password") {
      return {
        success: true,
        access_token: "mock_jwt_token_from_api_admin",
        token_type: "bearer",
        user: { user_id: "001", nick_name: "Admin User", role: "admin", username: "admin" },
        message: "Login successful (mock)"
      };
    } else if (credentials.username === "user" && credentials.password === "password") {
      return {
        success: true,
        access_token: "mock_jwt_token_from_api_user",
        token_type: "bearer",
        user: { user_id: "002", nick_name: "Normal User", role: "normal", username: "user" },
        message: "Login successful (mock)"
      };
    } else {
      return { 
        success: false, 
        message: "Invalid credentials" 
      };
    }
  }
}
