import { motion } from "framer-motion";
import { Clock, Shield, MessageSquare, FileCheck, Zap, Users } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslation } from "@/contexts/LanguageContext";

export const FeaturesSection = () => {
  const { t } = useTranslation();
  const features = [
    {
      icon: Clock,
      title: t("feature1Title"),
      description: t("feature1Desc"),
    },
    {
      icon: MessageSquare,
      title: t("feature2Title"),
      description: t("feature2Desc"),
    },
    {
      icon: Shield,
      title: t("feature3Title"),
      description: t("feature3Desc"),
    },
    {
      icon: FileCheck,
      title: t("feature4Title"),
      description: t("feature4Desc"),
    },
    {
      icon: Zap,
      title: t("feature5Title"),
      description: t("feature5Desc"),
    },
    {
      icon: Users,
      title: t("feature6Title"),
      description: t("feature6Desc"),
    },
  ];
  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            {t("powerfulFeaturesTitle")}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            {t("powerfulFeaturesDesc")}
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <Card variant="glass" className="h-full hover:shadow-xl hover:shadow-primary/10 hover:-translate-y-1 transition-all duration-300">
                <CardContent className="p-6">
                  <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-primary-foreground" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
