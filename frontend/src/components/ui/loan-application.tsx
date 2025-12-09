import { useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { Languages, Sun, Moon } from "lucide-react"
import { Button } from "@/components/ui/button"

export const LoanApplication = () => {
  const [emailOrPhone, setEmailOrPhone] = useState("")
  const [inputType, setInputType] = useState<"email" | "phone">("email")
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle")
  const [language, setLanguage] = useState<'en' | 'ta'>('en')
  const [darkMode, setDarkMode] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const navigate = useNavigate()

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    if (!darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!emailOrPhone) return

    setStatus("loading")

    setTimeout(() => {
      setStatus("success")
      setTimeout(() => {
        navigate("/dashboard")
      }, 2000)
    }, 1500)
  }

  const fireConfetti = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    const particles: Array<{
      x: number
      y: number
      vx: number
      vy: number
      life: number
      color: string
      size: number
    }> = []

    const colors = [
      "hsl(var(--primary))",
      "hsl(var(--success))",
      "hsl(var(--warning))",
      "hsl(var(--accent))",
      "hsl(var(--primary-foreground))"
    ]

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    const createParticle = () => {
      return {
        x: canvas.width / 2,
        y: canvas.height / 2,
        vx: (Math.random() - 0.5) * 12,
        vy: (Math.random() - 2) * 10,
        life: 100,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 4 + 2,
      }
    }

    for (let i = 0; i < 50; i++) {
      particles.push(createParticle())
    }

    const animate = () => {
      if (particles.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        return
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]
        p.x += p.vx
        p.y += p.vy
        p.vy += 0.5
        p.life -= 2

        ctx.fillStyle = p.color
        ctx.globalAlpha = Math.max(0, p.life / 100)
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()

        if (p.life <= 0) {
          particles.splice(i, 1)
          i--
        }
      }

      requestAnimationFrame(animate)
    }

    animate()
  }

  return (
    <>
      {/* Header Controls */}
      <header className="fixed top-0 right-0 z-50 p-4">
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={toggleDarkMode}
            title={darkMode ? (language === 'en' ? 'Switch to Light Mode' : 'ஒளி முறைக்கு மாற்று') : (language === 'en' ? 'Switch to Dark Mode' : 'இருள் முறைக்கு மாற்று')}
            className="bg-card/95 backdrop-blur"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setLanguage(language === 'en' ? 'ta' : 'en')}
            title={language === 'en' ? 'Switch to Tamil' : 'English-க்கு மாற்று'}
            className="bg-card/95 backdrop-blur"
          >
            <Languages className="w-4 h-4" />
          </Button>
        </div>
      </header>

      <div className="w-full min-h-screen bg-background flex items-center justify-center">
        <style>{`
          @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
          .animate-spin-slow { animation: spin-slow 60s linear infinite; }
          @keyframes spin-slow-reverse { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }
          .animate-spin-slow-reverse { animation: spin-slow-reverse 60s linear infinite; }
          @keyframes bounce-in { 0% { transform: scale(0.8); opacity: 0; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(1); opacity: 1; } }
          .animate-bounce-in { animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
          @keyframes success-pulse { 0% { transform: scale(0.5); opacity: 0; } 50% { transform: scale(1.1); } 70% { transform: scale(0.95); } 100% { transform: scale(1); opacity: 1; } }
          @keyframes success-glow { 0%, 100% { box-shadow: 0 0 20px hsl(var(--success) / 0.4); } 50% { box-shadow: 0 0 60px hsl(var(--success) / 0.8), 0 0 100px hsl(var(--success) / 0.4); } }
          @keyframes checkmark-draw { 0% { stroke-dashoffset: 24; } 100% { stroke-dashoffset: 0; } }
          @keyframes celebration-ring { 0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; } 100% { transform: translate(-50%, -50%) scale(2); opacity: 0; } }
          .animate-success-pulse { animation: success-pulse 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
          .animate-success-glow { animation: success-glow 2s ease-in-out infinite; }
          .animate-checkmark { stroke-dasharray: 24; stroke-dashoffset: 24; animation: checkmark-draw 0.4s ease-out 0.3s forwards; }
          .animate-ring { animation: celebration-ring 0.8s ease-out forwards; }
        `}</style>

        <div className="relative w-full h-screen overflow-hidden shadow-2xl" style={{ backgroundColor: 'hsl(var(--background))', fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
          <div className="absolute inset-0 w-full h-full pointer-events-none" style={{ perspective: "1200px", transform: "perspective(1200px) rotateX(15deg)", transformOrigin: "center bottom", opacity: 1 }}>
            <div className="absolute inset-0 animate-spin-slow" style={{ width: "2000px", height: "2000px", transform: "translate(-50%, -50%) rotate(279.05deg)", zIndex: 0, top: "50%", left: "50%" }}>
              <img src="https://framerusercontent.com/images/oqZEqzDEgSLygmUDuZAYNh2XQ9U.png?scale-down-to=2048" alt="" className="w-full h-full object-cover opacity-20" />
            </div>
            <div className="absolute inset-0 animate-spin-slow-reverse" style={{ width: "1000px", height: "1000px", transform: "translate(-50%, -50%) rotate(304.42deg)", zIndex: 1, top: "50%", left: "50%" }}>
              <img src="https://framerusercontent.com/images/UbucGYsHDAUHfaGZNjwyCzViw8.png?scale-down-to=1024" alt="" className="w-full h-full object-cover opacity-30" />
            </div>
            <div className="absolute inset-0 animate-spin-slow" style={{ width: "800px", height: "800px", transform: "translate(-50%, -50%) rotate(48.33deg)", zIndex: 2, top: "50%", left: "50%" }}>
              <img src="https://framerusercontent.com/images/Ans5PAxtJfg3CwxlrPMSshx2Pqc.png" alt="App Icon" className="w-full h-full object-cover opacity-40" />
            </div>
          </div>

          <div className="absolute inset-0 z-10 pointer-events-none" style={{ background: `linear-gradient(to top, hsl(var(--background)) 10%, hsla(var(--background) / 0.8) 40%, transparent 100%)` }} />

          <div className="relative z-20 w-full h-full flex flex-col items-center justify-end pb-24 gap-6">
            <div className="w-16 h-16 rounded-2xl shadow-lg overflow-hidden mb-2 ring-1 ring-border/10">
              <img src="https://images.unsplash.com/photo-1684369175833-4b445ad6bfb5?q=80&w=1696&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="App Icon" className="w-full h-full object-cover" />
            </div>

            <h1 className="text-5xl md:text-6xl font-bold text-center tracking-tight text-foreground">
              AI-Powered Loan Approval
            </h1>

            <p className="text-lg font-medium text-muted-foreground">
              Streamline loan approvals with intelligent agentic AI for Tata
            </p>

            <div className="flex gap-2 mb-4">
              <button
                type="button"
                onClick={() => setInputType("email")}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${inputType === "email" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80"}`}
              >
                Email
              </button>
              <button
                type="button"
                onClick={() => setInputType("phone")}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${inputType === "phone" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80"}`}
              >
                Phone
              </button>
            </div>

            <div className="w-full max-w-md px-4 mt-4 h-[60px] relative perspective-1000">
              <canvas ref={canvasRef} className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] pointer-events-none z-50" />

              <div className={`absolute inset-0 flex items-center justify-center rounded-full transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] ${status === "success" ? "opacity-100 scale-100 rotate-x-0 animate-success-pulse animate-success-glow" : "opacity-0 scale-95 -rotate-x-90 pointer-events-none"}`} style={{ backgroundColor: 'hsl(var(--success))', boxShadow: 'var(--shadow-glow)' }}>
                {status === "success" && (
                  <>
                    <div className="absolute top-1/2 left-1/2 w-full h-full rounded-full border-2 animate-ring opacity-70" style={{ borderColor: 'hsl(var(--success) / 0.8)', animationDelay: "0s" }} />
                    <div className="absolute top-1/2 left-1/2 w-full h-full rounded-full border-2 animate-ring opacity-50" style={{ borderColor: 'hsl(var(--success) / 0.6)', animationDelay: "0.15s" }} />
                    <div className="absolute top-1/2 left-1/2 w-full h-full rounded-full border-2 animate-ring opacity-30" style={{ borderColor: 'hsl(var(--success) / 0.4)', animationDelay: "0.3s" }} />
                  </>
                )}
                <div className={`flex items-center gap-2 text-primary-foreground font-semibold text-lg ${status === "success" ? "animate-bounce-in" : ""}`}>
                  <div className="bg-primary-foreground/20 p-1 rounded-full">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path className={status === "success" ? "animate-checkmark" : ""} strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span>Welcome! Redirecting to dashboard...</span>
                </div>
              </div>

              <form onSubmit={handleSubmit} className={`relative w-full h-full group transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] ${status === "success" ? "opacity-0 scale-95 rotate-x-90 pointer-events-none" : "opacity-100 scale-100 rotate-x-0"}`}>
                <input
                  type={inputType === "email" ? "email" : "tel"}
                  required
                  placeholder={inputType === "email" ? "name@email.com" : "+91 9876543210"}
                  value={emailOrPhone}
                  disabled={status === "loading"}
                  onChange={(e) => setEmailOrPhone(e.target.value)}
                  className="w-full h-[60px] pl-6 pr-[150px] rounded-full outline-none transition-all duration-200 placeholder-muted-foreground disabled:opacity-70 disabled:cursor-not-allowed bg-input border border-border text-foreground focus:ring-2 focus:ring-ring"
                />
                <div className="absolute top-[6px] right-[6px] bottom-[6px]">
                  <button type="submit" disabled={status === "loading"} className="h-full px-6 rounded-full font-medium text-primary-foreground transition-all active:scale-95 hover:bg-primary/90 disabled:hover:bg-primary disabled:active:scale-100 disabled:cursor-wait flex items-center justify-center min-w-[130px] bg-primary">
                    {status === "loading" ? (
                      <svg className="animate-spin h-5 w-5 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : (
                      "Start Application"
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default LoanApplication
