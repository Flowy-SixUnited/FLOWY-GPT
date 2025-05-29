import { ChatContext, ChatContextProvider } from '@/app/chat-context';
import SideBar from '@/components/layout/side-bar';
import FloatHelper from '@/new-components/layout/FloatHelper';
import { STORAGE_LANG_KEY, STORAGE_USERINFO_KEY, STORAGE_USERINFO_VALID_TIME_KEY } from '@/utils/constants/index';
import { App, ConfigProvider, MappingAlgorithm, theme, Spin } from 'antd';
import enUS from 'antd/locale/en_US';
import zhCN from 'antd/locale/zh_CN';
import classNames from 'classnames';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import { useRouter } from 'next/router';
import React, { useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import '../app/i18n';
import '../nprogress.css';
import '../styles/globals.css';
// import TopProgressBar from '@/components/layout/top-progress-bar';

const antdDarkTheme: MappingAlgorithm = (seedToken: any, mapToken: any) => {
  return {
    ...theme.darkAlgorithm(seedToken, mapToken),
    colorBgBase: '#232734',
    colorBorder: '#828282',
    colorBgContainer: '#232734',
  };
};

function CssWrapper({ children }: { children: React.ReactElement }) {
  const { mode } = useContext(ChatContext);
  const { i18n } = useTranslation();

  useEffect(() => {
    if (mode) {
      document.body?.classList?.add(mode);
      if (mode === 'light') {
        document.body?.classList?.remove('dark');
      } else {
        document.body?.classList?.remove('light');
      }
    }
  }, [mode]);

  useEffect(() => {
    i18n.changeLanguage?.(window.localStorage.getItem(STORAGE_LANG_KEY) || 'zh');
  }, [i18n]);

  return (
    <div>
      {/* <TopProgressBar /> */}
      {children}
    </div>
  );
}

function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const { isMenuExpand, mode } = useContext(ChatContext);
  const { i18n } = useTranslation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const router = useRouter();

  const AUTH_TOKEN_KEY = 'authToken';
  const USER_INFO_KEY = 'userInfo';

  // 检查认证状态
  useEffect(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      // TODO: 可选但推荐 - 向后端发送请求验证token的有效性
      // 如果验证通过:
      setIsAuthenticated(true);
      // 同步用户信息到旧的存储格式以保持兼容性
      const userInfo = localStorage.getItem(USER_INFO_KEY);
      if (userInfo && !localStorage.getItem(STORAGE_USERINFO_KEY)) {
        const user = JSON.parse(userInfo);
        // 转换为旧格式
        const legacyUser = {
          user_channel: user.username || 'dbgpt',
          user_no: user.user_id || '001',
          nick_name: user.nick_name || user.username || 'dbgpt',
        };
        localStorage.setItem(STORAGE_USERINFO_KEY, JSON.stringify(legacyUser));
        localStorage.setItem(STORAGE_USERINFO_VALID_TIME_KEY, Date.now().toString());
      }
    } else {
      setIsAuthenticated(false);
    }
    setAuthLoading(false);
  }, []);

  // 路由保护
  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated && router.pathname !== '/login') {
        router.push(`/login?redirect=${encodeURIComponent(router.asPath)}`);
      } else if (isAuthenticated && router.pathname === '/login') {
        // 如果已认证但试图访问登录页，则重定向到首页
        router.push('/');
      }
    }
  }, [authLoading, isAuthenticated, router.pathname, router.asPath, router]);

  if (authLoading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />;
  }

  // 如果未认证且不是登录页，则显示加载状态 (因为会被重定向)
  if (!isAuthenticated && router.pathname !== '/login') {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />;
  }

  const renderContent = () => {
    if (router.pathname.includes('mobile')) {
      return <>{children}</>;
    }
    return (
      <div className='flex w-screen h-screen overflow-hidden'>
        <Head>
          <meta name='viewport' content='initial-scale=1.0, width=device-width, maximum-scale=1' />
        </Head>
        {router.pathname !== '/construct/app/extra' && router.pathname !== '/login' && (
          <div className={classNames('transition-[width]', isMenuExpand ? 'w-60' : 'w-20', 'hidden', 'md:block')}>
            <SideBar />
          </div>
        )}
        <div className='flex flex-col flex-1 relative overflow-hidden'>{children}</div>
        {router.pathname !== '/login' && <FloatHelper />}
      </div>
    );
  };
  return (
    <ConfigProvider
      locale={i18n.language === 'en' ? enUS : zhCN}
      theme={{
        token: {
          colorPrimary: '#0C75FC',
          borderRadius: 4,
        },
        algorithm: mode === 'dark' ? antdDarkTheme : undefined,
      }}
    >
      <App>{renderContent()}</App>
    </ConfigProvider>
  );
}

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ChatContextProvider>
      <CssWrapper>
        <LayoutWrapper>
          <Component {...pageProps} />
        </LayoutWrapper>
      </CssWrapper>
    </ChatContextProvider>
  );
}

export default MyApp;
