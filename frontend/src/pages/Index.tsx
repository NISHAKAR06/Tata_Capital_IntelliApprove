import { Helmet } from 'react-helmet-async';
import LoanChatbot from '@/components/LoanChatbot';

const Index = () => {
  return (
    <>
      <Helmet>
        <title>AI Loan Assistant | Smart Banking Solutions</title>
        <meta name="description" content="Get instant loan approval with our AI-powered assistant. Personal loans, home loans, and business loans with transparent decision-making." />
      </Helmet>
      <LoanChatbot />
    </>
  );
};

export default Index;
