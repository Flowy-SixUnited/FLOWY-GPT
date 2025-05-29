import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Button, Input, Form, message, Card, Typography, Spin } from 'antd';
import { loginUser } from '@/client/api';

const { Title } = Typography;

const LoginPage: React.FC = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await loginUser({ username: values.username, password: values.password });
      
      if (response.success && response.access_token) {
        localStorage.setItem('authToken', response.access_token); // 存储认证Token
        localStorage.setItem('userInfo', JSON.stringify(response.user)); // 存储用户信息
        message.success('登录成功!');
        // 根据实际情况跳转到首页或之前的页面
        const redirectUrl = (router.query.redirect as string) || '/';
        router.push(redirectUrl);
      } else {
        message.error(response.message || '登录失败，请检查用户名或密码');
      }
    } catch (error) {
      console.error('登录请求失败:', error);
      message.error('登录请求失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <Title level={2}>用户登录</Title>
        </div>
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input placeholder="用户名" size="large" />
          </Form.Item>

          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password placeholder="密码" size="large" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }} size="large">
              登录
            </Button>
          </Form.Item>
        </Form>
        
        <div style={{ textAlign: 'center', marginTop: '16px', color: '#666', fontSize: '12px' }}>
          <p>测试账号:</p>
          <p>管理员: admin / password</p>
          <p>普通用户: user / password</p>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;
