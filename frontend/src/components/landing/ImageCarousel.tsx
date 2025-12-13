import { useEffect, useRef } from "react";
import useEmblaCarousel from "embla-carousel-react";
import Autoplay from "embla-carousel-autoplay";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/contexts/LanguageContext";

export const ImageCarousel = () => {
  const { t } = useTranslation();
  const autoplayRef = useRef(Autoplay({ delay: 5000, stopOnInteraction: false }));
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true }, [autoplayRef.current]);

  const scrollPrev = () => emblaApi?.scrollPrev();
  const scrollNext = () => emblaApi?.scrollNext();

  const slides = [
    {
      title: t("slide1Title"),
      description: t("slide1Desc"),
      gradient: "from-primary/90 to-accent/90",
    },
    {
      title: t("slide2Title"),
      description: t("slide2Desc"),
      gradient: "from-accent/90 to-primary/90",
    },
    {
      title: t("slide3Title"),
      description: t("slide3Desc"),
      gradient: "from-primary/80 to-tata-blue-light/90",
    },
    {
      title: t("slide4Title"),
      description: t("slide4Desc"),
      gradient: "from-tata-blue-dark/90 to-primary/90",
    },
  ];

  return (
    <section className="py-20 bg-secondary/30">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            {t("whyChooseIntelliApprove")}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            {t("carouselDescription")}
          </p>
        </motion.div>

        <div className="relative">
          <div className="overflow-hidden rounded-2xl" ref={emblaRef}>
            <div className="flex">
              {slides.map((slide, index) => (
                <div key={index} className="flex-[0_0_100%] min-w-0 px-2">
                  <div
                    className={`relative h-[400px] md:h-[500px] rounded-2xl bg-gradient-to-br ${slide.gradient} flex items-center justify-center overflow-hidden`}
                  >
                    {/* Background Pattern */}
                    <div className="absolute inset-0 opacity-10">
                      <div className="absolute top-0 left-0 w-full h-full">
                        {[...Array(20)].map((_, i) => (
                          <div
                            key={i}
                            className="absolute rounded-full bg-white/20"
                            style={{
                              width: Math.random() * 100 + 50,
                              height: Math.random() * 100 + 50,
                              left: `${Math.random() * 100}%`,
                              top: `${Math.random() * 100}%`,
                            }}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="relative z-10 text-center text-primary-foreground px-8 md:px-16 max-w-3xl">
                      <motion.h3
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-2xl md:text-4xl font-bold mb-4"
                      >
                        {slide.title}
                      </motion.h3>
                      <p className="text-lg md:text-xl opacity-90">
                        {slide.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Navigation Arrows */}
          <Button
            variant="glass"
            size="icon"
            className="absolute left-4 top-1/2 -translate-y-1/2 z-10 rounded-full"
            onClick={scrollPrev}
          >
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <Button
            variant="glass"
            size="icon"
            className="absolute right-4 top-1/2 -translate-y-1/2 z-10 rounded-full"
            onClick={scrollNext}
          >
            <ChevronRight className="w-5 h-5" />
          </Button>

          {/* Dots */}
          <div className="flex justify-center gap-2 mt-6">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => emblaApi?.scrollTo(index)}
                className="w-3 h-3 rounded-full bg-primary/30 hover:bg-primary/60 transition-colors data-[active=true]:bg-primary"
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
