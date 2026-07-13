import Nav from './components/landing/Nav';
import Hero from './components/landing/Hero';
import TheorySection from './components/landing/TheorySection';
import FeatureGrid from './components/landing/FeatureGrid';
import FormatsAndDepth from './components/landing/FormatsAndDepth';
import Footer from './components/landing/Footer';

// Landing page -- a Server Component (no 'use client') so it can rely on
// root layout.js's metadata for SEO without fighting the client-component
// metadata-export restriction. The actual tool lives at /app.
export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Nav />
      <Hero />
      <TheorySection />
      <FeatureGrid />
      <FormatsAndDepth />
      <Footer />
    </div>
  );
}
