import { Link } from 'react-router-dom';
import { Button } from '@/components/common/Button';
import { DecorativeBlobs } from '@/components/common/DecorativeBlobs';
import { useScrollReveal } from '@/hooks/useScrollReveal';
import { ROUTES } from '@/config/routes';
import { Zap, UtensilsCrossed, Clock, Phone, Star, Sparkles } from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'Instant Setup',
    description: 'Get a dedicated phone number in minutes and start answering calls right away.',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50',
  },
  {
    icon: UtensilsCrossed,
    title: 'Menu-Aware AI',
    description: 'Your assistant knows every item, price, and modifier so it can answer any question.',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
  },
  {
    icon: Clock,
    title: '24/7 Availability',
    description: "Take orders even when you're closed with round-the-clock phone coverage.",
    color: 'text-secondary',
    bgColor: 'bg-secondary/10',
  },
  {
    icon: Phone,
    title: 'Call History',
    description: 'Review every conversation and transcript to understand what guests are asking for.',
    color: 'text-success',
    bgColor: 'bg-success/10',
  },
];

const howItWorks = [
  {
    step: '01',
    title: 'Sign up in one step',
    description: 'Create your restaurant and team account at the same time. Your phone number is ready instantly.',
  },
  {
    step: '02',
    title: 'Add your menu',
    description: 'Import categories, items, modifiers, and images so the AI can guide callers through your offering.',
  },
  {
    step: '03',
    title: 'Set your hours',
    description: 'Define operating hours, holiday overrides, and delivery zones in just a few clicks.',
  },
  {
    step: '04',
    title: 'Start receiving calls',
    description: 'Route every caller to your AI assistant who knows your menu and handles orders start to finish.',
  },
];

export const LandingPage = () => {
  const heroRef = useScrollReveal();
  const socialProofRef = useScrollReveal();
  const featuresRef = useScrollReveal();
  const testimonialRef = useScrollReveal();
  const howItWorksRef = useScrollReveal();
  const ctaRef = useScrollReveal();

  return (
    <div className="min-h-screen bg-background text-gray-900">
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-linear-to-br from-primary/10 via-white to-secondary/10" />
        <DecorativeBlobs />

        {/* Header */}
        <header className="relative z-10 border-b border-primary/10 bg-white/80 backdrop-blur">
          <div className="container mx-auto flex items-center justify-between px-4 py-4 md:py-5">
            <Link to={ROUTES.LANDING} className="text-lg font-semibold text-primary sm:text-xl md:text-2xl">
              CallEats
            </Link>
            <nav className="hidden items-center gap-6 text-sm font-medium text-gray-700 lg:flex">
              <a href="#features" className="hover:text-primary">
                Features
              </a>
              <a href="#how-it-works" className="hover:text-primary">
                How it works
              </a>
              <a href="#pricing" className="hover:text-primary">
                Pricing
              </a>
            </nav>
            <div className="flex items-center gap-2 sm:gap-3">
              <Link to={ROUTES.LOGIN} className="hidden sm:block">
                <Button variant="outline" size="sm" className="sm:hidden md:flex">
                  Sign In
                </Button>
              </Link>
              <Link to={ROUTES.SIGNUP}>
                <Button variant="primary" size="sm" className="text-sm sm:text-base md:size-md">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="relative z-10">
          <div className="container mx-auto grid items-center gap-8 px-4 py-12 sm:gap-12 sm:py-16 md:grid-cols-2 md:py-24 lg:gap-16">
            <div ref={heroRef.ref} className={`space-y-6 sm:space-y-8 reveal-slide-right ${heroRef.isVisible ? 'is-visible' : ''}`}>
              <div className="inline-flex items-center gap-2 rounded-full bg-linear-to-r from-primary/20 to-secondary/20 px-3 py-1.5 text-xs font-medium text-primary shadow-sm backdrop-blur sm:px-4 sm:py-2 sm:text-sm">
                <Sparkles className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="font-semibold">New</span>
                <span className="hidden text-gray-700 sm:inline">Trusted by 500+ restaurants</span>
              </div>
              <h1 className="text-3xl font-bold leading-tight sm:text-4xl md:text-5xl lg:text-6xl">
                Your Restaurant's AI Phone Assistant
              </h1>
              <p className="text-base text-gray-600 sm:text-lg md:text-xl">
                Never miss an order again. Our AI answers every call, knows your menu by heart, and books orders 24/7 so
                your team can focus on hospitality.
              </p>
              <div className="flex flex-col items-start gap-4 sm:flex-row">
                <Link to={ROUTES.SIGNUP}>
                  <Button variant="primary" size="lg">
                    Get Started Free
                  </Button>
                </Link>
                <a href="#how-it-works">
                  <Button variant="outline" size="lg">
                    See How It Works
                  </Button>
                </a>
              </div>
              <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <span className="font-medium">4.9/5 from restaurant teams</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
                  <span>No setup fee • Cancel anytime</span>
                </div>
              </div>
            </div>

            <div className="relative space-y-6">
              <div className="absolute inset-0 -translate-y-12 translate-x-12 rounded-3xl bg-linear-to-br from-primary/20 to-secondary/20 blur-3xl" />
              
              {/* Hero Image First */}
              <div className="relative mx-auto w-full max-w-6xl">
                <div className="relative overflow-hidden rounded-xl border-4 border-gray-800 bg-gray-800 shadow-2xl sm:rounded-2xl">
                  {/* Browser Chrome */}
                  <div className="flex h-10 items-center gap-2 bg-gray-700 px-3 sm:h-12 sm:px-4">
                    {/* Traffic Lights / Window Controls */}
                    <div className="flex gap-1.5 sm:gap-2">
                      <div className="h-2.5 w-2.5 rounded-full bg-red-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-yellow-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-green-500 sm:h-3 sm:w-3" />
                    </div>
                    {/* Address Bar */}
                    <div className="ml-2 flex flex-1 items-center gap-2 rounded-md bg-gray-600 px-3 py-1 sm:ml-4 sm:px-4 sm:py-1.5">
                      <div className="h-1.5 w-1.5 rounded-full bg-gray-400 sm:h-2 sm:w-2" />
                      <div className="h-1.5 flex-1 rounded bg-gray-500/50 sm:h-2" />
                    </div>
                  </div>
                  
                  {/* Screen Content - Hero Image */}
                  <div className="relative bg-white">
                    <img
                      src="/hero.png"
                      alt="CallEats Hero - AI voice assistant for restaurants"
                      className="w-full h-auto object-contain"
                      loading="lazy"
                    />
                  </div>
                </div>
              </div>

              {/* Dashboard Image Second */}
              <div className="relative mx-auto w-full max-w-6xl">
                <div className="relative overflow-hidden rounded-xl border-4 border-gray-800 bg-gray-800 shadow-2xl sm:rounded-2xl">
                  {/* Browser Chrome */}
                  <div className="flex h-10 items-center gap-2 bg-gray-700 px-3 sm:h-12 sm:px-4">
                    {/* Traffic Lights / Window Controls */}
                    <div className="flex gap-1.5 sm:gap-2">
                      <div className="h-2.5 w-2.5 rounded-full bg-red-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-yellow-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-green-500 sm:h-3 sm:w-3" />
                    </div>
                    {/* Address Bar */}
                    <div className="ml-2 flex flex-1 items-center gap-2 rounded-md bg-gray-600 px-3 py-1 sm:ml-4 sm:px-4 sm:py-1.5">
                      <div className="h-1.5 w-1.5 rounded-full bg-gray-400 sm:h-2 sm:w-2" />
                      <div className="h-1.5 flex-1 rounded bg-gray-500/50 sm:h-2" />
                    </div>
                  </div>
                  
                  {/* Screen Content - Dashboard Image */}
                  <div className="relative bg-white">
                    <img
                      src="/calleats.png"
                      alt="CallEats Dashboard - AI-powered restaurant voice assistant with call history, menu management, and real-time analytics"
                      className="w-full h-auto object-contain"
                      loading="lazy"
                    />
                  </div>
                </div>
              </div>

              {/* Menu Builder Image Third */}
              <div className="relative mx-auto w-full max-w-6xl">
                <div className="relative overflow-hidden rounded-xl border-4 border-gray-800 bg-gray-800 shadow-2xl sm:rounded-2xl">
                  {/* Browser Chrome */}
                  <div className="flex h-10 items-center gap-2 bg-gray-700 px-3 sm:h-12 sm:px-4">
                    {/* Traffic Lights / Window Controls */}
                    <div className="flex gap-1.5 sm:gap-2">
                      <div className="h-2.5 w-2.5 rounded-full bg-red-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-yellow-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-green-500 sm:h-3 sm:w-3" />
                    </div>
                    {/* Address Bar */}
                    <div className="ml-2 flex flex-1 items-center gap-2 rounded-md bg-gray-600 px-3 py-1 sm:ml-4 sm:px-4 sm:py-1.5">
                      <div className="h-1.5 w-1.5 rounded-full bg-gray-400 sm:h-2 sm:w-2" />
                      <div className="h-1.5 flex-1 rounded bg-gray-500/50 sm:h-2" />
                    </div>
                  </div>
                  
                  {/* Screen Content - Menu Builder Image */}
                  <div className="relative bg-white">
                    <img
                      src="/menu_builder.png"
                      alt="CallEats Menu Builder - Manage menu items, categories, and modifiers"
                      className="w-full h-auto object-contain"
                      loading="lazy"
                    />
                  </div>
                </div>
              </div>

              {/* Delivery Zones Image Fourth */}
              <div className="relative mx-auto w-full max-w-6xl">
                <div className="relative overflow-hidden rounded-xl border-4 border-gray-800 bg-gray-800 shadow-2xl sm:rounded-2xl">
                  {/* Browser Chrome */}
                  <div className="flex h-10 items-center gap-2 bg-gray-700 px-3 sm:h-12 sm:px-4">
                    {/* Traffic Lights / Window Controls */}
                    <div className="flex gap-1.5 sm:gap-2">
                      <div className="h-2.5 w-2.5 rounded-full bg-red-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-yellow-500 sm:h-3 sm:w-3" />
                      <div className="h-2.5 w-2.5 rounded-full bg-green-500 sm:h-3 sm:w-3" />
                    </div>
                    {/* Address Bar */}
                    <div className="ml-2 flex flex-1 items-center gap-2 rounded-md bg-gray-600 px-3 py-1 sm:ml-4 sm:px-4 sm:py-1.5">
                      <div className="h-1.5 w-1.5 rounded-full bg-gray-400 sm:h-2 sm:w-2" />
                      <div className="h-1.5 flex-1 rounded bg-gray-500/50 sm:h-2" />
                    </div>
                  </div>
                  
                  {/* Screen Content - Delivery Zones Image */}
                  <div className="relative bg-white">
                    <img
                      src="/zones.png"
                      alt="CallEats Delivery Zones - Configure delivery areas with interactive maps"
                      className="w-full h-auto object-contain"
                      loading="lazy"
                    />
                  </div>
                </div>
              </div>
              
              {/* Glow Effect */}
              <div className="absolute -inset-4 -z-10 rounded-2xl bg-linear-to-br from-primary/20 via-secondary/20 to-primary/20 blur-2xl opacity-75" />
            </div>
          </div>
        </section>
      </div>

      {/* Social Proof */}
      <section ref={socialProofRef.ref} className={`border-y border-primary/10 bg-white reveal-fade ${socialProofRef.isVisible ? 'is-visible' : ''}`}>
        <div className="container mx-auto flex flex-col items-center gap-6 px-4 py-10 text-center md:flex-row md:justify-between">
          <div className="text-lg font-semibold text-gray-700">Loved by restaurants nationwide</div>
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm font-medium text-gray-500">
            <span>Blue Harbor Bistro</span>
            <span>Urban Table</span>
            <span>Fiesta Cantina</span>
            <span>Green Bowl Co.</span>
            <span>Sunset Grill</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container mx-auto px-4 py-16 md:py-24 bg-dot-pattern">
        <div ref={featuresRef.ref} className={`mx-auto mb-12 max-w-2xl text-center reveal-slide-up ${featuresRef.isVisible ? 'is-visible' : ''}`}>
          <h2 className="text-3xl font-bold md:text-4xl">Built for fast-paced restaurant teams</h2>
          <p className="mt-4 text-gray-600">
            Every detail is designed for front-of-house efficiency — from instant setup to deep menu awareness and order
            accuracy.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            // Note: useScrollReveal hook cannot be called inside map callback
            // Animation will still work via CSS classes
            const delays = ['', 'delay-100', 'delay-200', 'delay-300'];
            const orbPositions = [
              '-right-8 -top-8',    // top-right
              '-left-8 -top-8',     // top-left  
              '-right-8 -bottom-8', // bottom-right
              '-left-8 -bottom-8'   // bottom-left
            ];
            return (
              <div 
                key={feature.title}
                className={`group relative flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-md transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:border-primary/30 reveal-slide-up ${delays[index]}`}
              >
                <div className={`absolute ${orbPositions[index]} h-24 w-24 rounded-full bg-linear-to-br from-primary/5 to-secondary/5 blur-2xl transition-all duration-300 group-hover:scale-150`} />
                <div className={`relative inline-flex h-16 w-16 items-center justify-center rounded-2xl ${feature.bgColor} transition-all duration-300 group-hover:scale-110 group-hover:rotate-3`}>
                  <IconComponent className={`h-8 w-8 ${feature.color}`} strokeWidth={2.5} />
                </div>
                <h3 className="relative mt-4 text-xl font-bold text-gray-900 sm:mt-5 sm:text-2xl">{feature.title}</h3>
                <p className="relative mt-2 grow text-sm leading-relaxed text-gray-700 sm:mt-3 sm:text-base">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Testimonial */}
      <section ref={testimonialRef.ref} className={`bg-secondary/5 reveal-fade ${testimonialRef.isVisible ? 'is-visible' : ''}`}>
        <div className="container mx-auto grid gap-10 px-4 py-16 md:grid-cols-2 md:items-center">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold md:text-4xl">“It feels like we added a full-time host.”</h2>
            <p className="text-lg text-gray-600">
              “Our callers get immediate answers, every order is captured, and the team spends more time with guests in the dining room. It paid for itself in the first weekend.”
            </p>
            <div className="text-sm font-semibold text-gray-700">— Sofia Martinez, Owner of Azul Cocina</div>
          </div>
          <div className="relative overflow-hidden rounded-3xl border border-gray-200 bg-linear-to-br from-white to-gray-50 p-6 shadow-xl sm:p-8">
            <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-linear-to-br from-secondary/5 to-success/5 blur-2xl" />
            <div className="relative mb-4 text-xs font-semibold uppercase tracking-wide text-secondary sm:mb-6">Example metrics</div>
            <dl className="relative grid grid-cols-2 gap-4 text-sm sm:gap-6 md:gap-8">
              <div className="space-y-1">
                <dt className="text-xs text-gray-600 sm:text-sm">Calls answered this week</dt>
                <dd className="text-2xl font-bold text-gray-900 sm:text-3xl">128</dd>
              </div>
              <div className="space-y-1">
                <dt className="text-xs text-gray-600 sm:text-sm">Orders booked</dt>
                <dd className="text-2xl font-bold text-gray-900 sm:text-3xl">93</dd>
              </div>
              <div className="space-y-1">
                <dt className="text-xs text-gray-600 sm:text-sm">Average response time</dt>
                <dd className="text-2xl font-bold text-secondary sm:text-3xl">0.8s</dd>
              </div>
              <div className="space-y-1">
                <dt className="text-xs text-gray-600 sm:text-sm">Customer satisfaction</dt>
                <dd className="text-2xl font-bold text-success sm:text-3xl">98%</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="container mx-auto px-4 py-16 md:py-24 bg-grid-pattern">
        <div ref={howItWorksRef.ref} className={`mx-auto mb-12 max-w-2xl text-center reveal-slide-up ${howItWorksRef.isVisible ? 'is-visible' : ''}`}>
          <p className="text-sm font-medium uppercase tracking-wide text-secondary">How it works</p>
          <h2 className="mt-3 text-3xl font-bold md:text-4xl">Launch your AI phone assistant in four steps</h2>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {howItWorks.map((item, index) => {
            const orbPositions = [
              '-right-6 -top-6',
              '-left-6 -top-6',
              '-right-6 -bottom-6',
              '-left-6 -bottom-6'
            ];
            return (
              <div key={item.step} className="group relative flex h-full flex-col gap-4 overflow-hidden rounded-2xl border border-gray-200 bg-white p-8 shadow-md transition-all duration-300 hover:shadow-xl hover:border-secondary/30">
                <div className={`absolute ${orbPositions[index]} h-24 w-24 rounded-full bg-linear-to-br from-secondary/10 to-primary/10 blur-xl transition-all duration-300 group-hover:scale-150`} />
                <div className="relative inline-flex h-16 w-16 items-center justify-center rounded-full bg-linear-to-br from-secondary to-secondary/80 text-2xl font-bold text-white shadow-lg ring-4 ring-secondary/10 transition-all duration-300 group-hover:ring-8 group-hover:ring-secondary/20">
                  {item.step}
                </div>
                <h3 className="relative text-xl font-bold text-gray-900 sm:text-2xl">{item.title}</h3>
                <p className="relative grow text-sm leading-relaxed text-gray-700 sm:text-base">{item.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Final CTA */}
      <section id="pricing" className="container mx-auto px-4 pb-16 md:pb-24">
        <div ref={ctaRef.ref} className={`relative overflow-hidden rounded-3xl bg-linear-to-br from-primary via-primary to-primary/90 text-white shadow-2xl reveal-slide-up ${ctaRef.isVisible ? 'is-visible' : ''}`}>
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-secondary/20 blur-3xl" />
          <div className="relative grid gap-8 p-10 md:grid-cols-2 md:items-center md:p-16">
            <div>
              <h2 className="text-3xl font-bold md:text-4xl">Ready to take every call?</h2>
              <p className="mt-4 text-primary/20">
                Launch your AI phone assistant today and start capturing every guest request.
              </p>
            </div>
            <div className="flex flex-col gap-4 md:flex-row md:justify-end">
              <Link to={ROUTES.SIGNUP}>
                <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-primary">
                  Start Free Trial
                </Button>
              </Link>
              <a href="mailto:hello@restaurant-voice-assistant.com">
                <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-primary">
                  Talk to Sales
                </Button>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-primary/10 bg-white">
        <div className="container mx-auto grid gap-8 px-4 py-8 sm:grid-cols-2 sm:gap-10 sm:py-12 lg:grid-cols-4">
          <div>
            <div className="text-lg font-semibold text-primary">CallEats</div>
            <p className="mt-3 text-sm text-gray-600">
              AI phone agents that know your menu, take orders, and delight every caller.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Product</h4>
            <ul className="mt-3 space-y-2 text-sm text-gray-600">
              <li><a href="#features" className="hover:text-primary">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-primary">How it works</a></li>
              <li><a href="#pricing" className="hover:text-primary">Pricing</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Resources</h4>
            <ul className="mt-3 space-y-2 text-sm text-gray-600">
              <li><Link to={ROUTES.LOGIN} className="hover:text-primary">Sign in</Link></li>
              <li><Link to={ROUTES.SIGNUP} className="hover:text-primary">Create account</Link></li>
              <li><a href="mailto:hello@restaurant-voice-assistant.com" className="hover:text-primary">Support</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Contact</h4>
            <ul className="mt-3 space-y-2 text-sm text-gray-600">
              <li>hello@restaurant-voice-assistant.com</li>
              <li>+1 (415) 555-1098</li>
              <li>San Francisco, CA</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-primary/10 py-6 text-center text-xs text-gray-500">
          © {new Date().getFullYear()} CallEats. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

