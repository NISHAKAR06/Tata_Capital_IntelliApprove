import { Layout } from "@/components/layout/Layout";
import { HeroSection } from "@/components/landing/HeroSection";
import { ImageCarousel } from "@/components/landing/ImageCarousel";
import { FeaturesSection } from "@/components/landing/FeaturesSection";

const Index = () => {
  return (
    <Layout>
      <HeroSection />
      <ImageCarousel />
      <FeaturesSection />
    </Layout>
  );
};

export default Index;
