import { Helmet } from 'react-helmet-async';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  Languages,
  Sun,
  Moon,
  Shield,
  Bell,
  Key,
  Mail,
  Phone,
  Save
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const Settings = () => {
  const [language, setLanguage] = useState<'en' | 'ta'>('en');
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [userInfo, setUserInfo] = useState({
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@email.com',
    phone: '+91 9876543210',
    address: 'Chennai, Tamil Nadu'
  });

  // Apply dark mode to document
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleSave = () => {
    // In a real app, this would save to backend
    alert(language === 'en' ? 'Settings saved successfully!' : 'அமைப்புகள் வெற்றிகரமாக சேமிக்கப்பட்டது!');
  };

  return (
    <>
      <Helmet>
        <title>Settings | AI Loan Assistant</title>
        <meta name="description" content="Personal settings and preferences for the loan application system." />
      </Helmet>

      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="sticky top-0 z-10 border-b border-border bg-card/95 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
            <Link
              to="/dashboard"
              className="p-2 hover:bg-muted rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-muted-foreground" />
            </Link>
            <div>
              <h1 className="text-xl font-semibold text-foreground">
                {language === 'en' ? 'Settings' : 'அமைப்புகள்'}
              </h1>
              <p className="text-sm text-muted-foreground">
                {language === 'en' ? 'Manage your preferences' : 'உங்கள் விருப்பங்களை நிர்வகிக்கவும்'}
              </p>
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-6 space-y-8">
          {/* 1. Profile Information */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="text-lg font-semibold text-foreground mb-6 flex items-center gap-2">
              <User className="w-5 h-5" />
              {language === 'en' ? 'Profile Information' : 'சுயவிவர தகவல்'}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  {language === 'en' ? 'Full Name' : 'முழு பெயர்'}
                </label>
                <input
                  type="text"
                  value={userInfo.name}
                  onChange={(e) => setUserInfo({...userInfo, name: e.target.value})}
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary outline-none"
                  placeholder="Enter your full name"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  {language === 'en' ? 'Email Address' : 'மின்னஞ்சல் முகவரி'}
                </label>
                <input
                  type="email"
                  value={userInfo.email}
                  onChange={(e) => setUserInfo({...userInfo, email: e.target.value})}
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary outline-none"
                  placeholder="Enter your email"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  {language === 'en' ? 'Phone Number' : 'தொலைபேசி எண்'}
                </label>
                <input
                  type="tel"
                  value={userInfo.phone}
                  onChange={(e) => setUserInfo({...userInfo, phone: e.target.value})}
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary outline-none"
                  placeholder="+91 9876543210"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">
                  {language === 'en' ? 'Address' : 'முகவரி'}
                </label>
                <input
                  type="text"
                  value={userInfo.address}
                  onChange={(e) => setUserInfo({...userInfo, address: e.target.value})}
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary outline-none"
                  placeholder="Enter your address"
                />
              </div>
            </div>
          </div>

          {/* 2. Preferences */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="text-lg font-semibold text-foreground mb-6 flex items-center gap-2">
              <Shield className="w-5 h-5" />
              {language === 'en' ? 'Preferences' : 'விருப்பங்கள்'}
            </h2>

            <div className="space-y-6">
              {/* Language */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Languages className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-foreground">
                      {language === 'en' ? 'Language' : 'மொழி'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {language === 'en'
                        ? 'Choose your preferred language'
                        : 'உங்கள் விருப்பமான மொழியை தேர்ந்தெடுக்கவும்'
                      }
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setLanguage('en')}
                    className={cn(
                      "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                      language === 'en'
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    )}
                  >
                    English
                  </button>
                  <button
                    onClick={() => setLanguage('ta')}
                    className={cn(
                      "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                      language === 'ta'
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    )}
                  >
                    தமிழ்
                  </button>
                </div>
              </div>

              {/* Dark Mode */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {darkMode ? <Moon className="w-5 h-5 text-muted-foreground" /> : <Sun className="w-5 h-5 text-muted-foreground" />}
                  <div>
                    <p className="font-medium text-foreground">
                      {darkMode ? (language === 'en' ? 'Dark Mode' : 'இருள் முறை') : (language === 'en' ? 'Light Mode' : 'ஒளி முறை')}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {language === 'en'
                        ? 'Toggle between light and dark themes'
                        : 'ஒளி மற்றும் இருள் கருப்பொருள்களுக்கு இடையில் மாற்றவும்'
                      }
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleDarkMode}
                  className="gap-2"
                >
                  {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                  {darkMode ? (language === 'en' ? 'Switch to Light' : 'ஒளிக்கு மாற்று') : (language === 'en' ? 'Switch to Dark' : 'இருளுக்கு மாற்று')}
                </Button>
              </div>

              {/* Notifications */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-foreground">
                      {language === 'en' ? 'Notifications' : 'அறிவிப்புகள்'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {language === 'en'
                        ? 'Receive updates about your loan applications'
                        : 'உங்கள் கடன் விண்ணப்பங்கள் பற்றிய புதுப்பிப்புகளைப் பெறுங்கள்'
                      }
                    </p>
                  </div>
                </div>
                <Button
                  variant={notifications ? "default" : "outline"}
                  size="sm"
                  onClick={() => setNotifications(!notifications)}
                  className="gap-2"
                >
                  <Bell className="w-4 h-4" />
                  {notifications ? (language === 'en' ? 'Enabled' : 'இயக்கப்பட்டது') : (language === 'en' ? 'Disabled' : 'முடக்கப்பட்டது')}
                </Button>
              </div>
            </div>
          </div>

          {/* 3. Security */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="text-lg font-semibold text-foreground mb-6 flex items-center gap-2">
              <Key className="w-5 h-5" />
              {language === 'en' ? 'Security' : 'பாதுகாப்பு'}
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-foreground">
                      {language === 'en' ? 'Change Password' : 'கடவுச்சொல்லை மாற்று'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {language === 'en'
                        ? 'Update your account password'
                        : 'உங்கள் கணக்கு கடவுச்சொல்லை புதுப்பிக்கவும்'
                      }
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  {language === 'en' ? 'Update' : 'புதுப்பிக்கு'}
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-foreground">
                      {language === 'en' ? 'Two-Factor Authentication' : 'இரண்டு காரணி அங்கீகாரம்'}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {language === 'en'
                        ? 'Add an extra layer of security'
                        : 'பாதுகாப்பின் கூடுதல் அடுக்கைச் சேர்க்கவும்'
                      }
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  {language === 'en' ? 'Enable' : 'இயக்கு'}
                </Button>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={handleSave} className="gap-2">
              <Save className="w-4 h-4" />
              {language === 'en' ? 'Save Changes' : 'மாற்றங்களை சேமிக்கு'}
            </Button>
          </div>
        </main>
      </div>
    </>
  );
};

export default Settings;
