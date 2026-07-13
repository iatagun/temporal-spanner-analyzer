import Link from 'next/link';
import CliqueSpannerDiagram from '../CliqueSpannerDiagram';

export default function Hero() {
  return (
    <section className="max-w-5xl mx-auto px-6 pt-16 pb-12 text-center">
      <h1 className="font-serif text-4xl sm:text-5xl font-medium tracking-tight text-gray-900 dark:text-gray-100 mb-5 max-w-3xl mx-auto">
        Derlemde kavramların zamanla nasıl evrildiğini görün
      </h1>
      <p className="text-base text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed mb-8">
        Baligács (2026) lineer spanner algoritmasıyla kelime birlikteliklerini
        seyrek zamanlı çizgelere indirger; kavram kümelerinin doğum, büyüme ve
        kayboluş süreçlerini görünür kılar.
      </p>
      <div className="flex items-center justify-center gap-3 mb-14">
        <Link href="/app"
          className="px-5 py-2.5 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 transition-colors">
          Aracı Aç
        </Link>
        <Link href="/app?sample=1"
          className="px-5 py-2.5 border border-gray-300 dark:border-gray-700 text-sm text-gray-600 dark:text-gray-300 font-medium rounded-md hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
          Örnek Veri ile Dene
        </Link>
      </div>
      <CliqueSpannerDiagram className="w-full max-w-md h-auto mx-auto text-gray-400 dark:text-gray-600" />
    </section>
  );
}
