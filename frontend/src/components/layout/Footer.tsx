import { Link } from "react-router-dom";
import { useTranslation } from "@/contexts/LanguageContext";

export const Footer = () => {
  const { t } = useTranslation();
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand */}
          <div>
            <Link to="/" className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg font-poppins">IA</span>
              </div>
              <div>
                <span className="font-poppins font-bold text-xl">Intelli</span>
                <span className="font-poppins font-bold text-xl text-primary">Approve</span>
              </div>
            </Link>
            <p className="text-background/70 text-sm leading-relaxed">
              {t("footerDesc")}
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-poppins font-semibold text-lg mb-4">{t("quickLinks")}</h4>
            <ul className="space-y-3">
              {[].map((item) => (
                <li key={item}>
                  <Link
                    to={`/${item.toLowerCase().replace(" ", "-")}`}
                    className="text-background/70 hover:text-background transition-colors text-sm"
                  >
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="font-poppins font-semibold text-lg mb-4">{t("services")}</h4>
            <ul className="space-y-3">
              <li>
                <span className="text-background/70 text-sm">{t("personalLoans")}</span>
              </li>
              <li>
                <span className="text-background/70 text-sm">{t("aiAssistantFooter")}</span>
              </li>
              <li>
                <span className="text-background/70 text-sm">{t("quickApproval")}</span>
              </li>
              <li>
                <span className="text-background/70 text-sm">{t("documentUpload")}</span>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-poppins font-semibold text-lg mb-4">{t("contact")}</h4>
            <ul className="space-y-3 text-background/70 text-sm">
              <li>{t("supportEmail")}</li>
              <li>{t("supportPhone")}</li>
              <li>{t("supportLocation")}</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-background/20 mt-12 pt-8 text-center">
          <p className="text-background/60 text-sm">
            {t("copyright")}
          </p>
        </div>
      </div>
    </footer>
  );
};
