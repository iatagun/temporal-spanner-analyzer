'use client';

export default function RightSidebar() {
  return (
    <aside className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed space-y-5">
      <div>
        <h3 className="font-serif text-sm font-medium text-gray-700 dark:text-gray-300 tracking-tight mb-2">
          Kullanım
        </h3>
      </div>

      <div>
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-1">Dosya Sürükle</h4>
        <p>
          .conllu, .vrt, .csv veya .json dosyanızı sürükleyin ya da
          &ldquo;Dosya Seç&rdquo; ile yükleyin. &ldquo;Örnek Veri ile Dene&rdquo;
          hazır bir derlemle aracı keşfetmenizi sağlar.
        </p>
      </div>

      <div>
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-1">Görünümler</h4>
        <ul className="space-y-1">
          <li><strong className="text-gray-700 dark:text-gray-300">Spanner</strong> &mdash; Orijinal ve seyreltilmiş çizge</li>
          <li><strong className="text-gray-700 dark:text-gray-300">Trendler</strong> &mdash; Kliklerin zaman çizelgesi</li>
          <li><strong className="text-gray-700 dark:text-gray-300">Karşılaştır</strong> &mdash; İki dönem yan yana</li>
          <li><strong className="text-gray-700 dark:text-gray-300">Keşfet</strong> &mdash; Kelime ve klik sorgulama</li>
        </ul>
      </div>

      <div className="pt-3 border-t border-gray-100 dark:border-gray-800">
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-2">
          Dosya Şablonları
        </h4>

        <div className="space-y-3">
          <div>
            <span className="text-[10px] font-semibold text-gray-600 dark:text-gray-400 uppercase">CoNLL-U</span>
            <pre className="mt-1 text-[10px] rounded-md bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-2 overflow-x-auto text-gray-600 dark:text-gray-400">
{`# date = 2020-01-15
1\tyapay\tyapay\tADJ
2\tzeka\tzeka\tNOUN
3\tveri\tveri\tNOUN

# date = 2020-06-10
1\tyapay\tyapay\tADJ
2\tdil\tdil\tNOUN`}
            </pre>
            <p className="mt-0.5 text-gray-400 dark:text-gray-500">Sütun 2 (FORM) veya 3 (LEMMA) okunur. <code># date =</code> satırı zamanı belirler.</p>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-gray-600 dark:text-gray-400 uppercase">CSV</span>
            <pre className="mt-1 text-[10px] rounded-md bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-2 overflow-x-auto text-gray-600 dark:text-gray-400">
{`date,words
2020-01-15,"yapay,zeka,veri"
2020-06-10,"yapay,dil,isleme"`}
            </pre>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-gray-600 dark:text-gray-400 uppercase">JSON</span>
            <pre className="mt-1 text-[10px] rounded-md bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-2 overflow-x-auto text-gray-600 dark:text-gray-400">
{`[
  {"date":"2020-01-15","words":["yapay","zeka"]},
  {"date":"2020-06-10","words":["yapay","dil"]}
]`}
            </pre>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-gray-600 dark:text-gray-400 uppercase">VRT</span>
            <pre className="mt-1 text-[10px] rounded-md bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 p-2 overflow-x-auto text-gray-600 dark:text-gray-400">
{`<text date="2020-01-15">
yapay\tADJ
zeka\tNOUN
veri\tNOUN
</text>`}
            </pre>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-gray-100 dark:border-gray-800">
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-1">Yorumlama</h4>
        <p>
          <strong className="text-gray-700 dark:text-gray-300">Tasarruf %</strong> yüksekse ilişkiler bağımlı.{' '}
          <strong className="text-gray-700 dark:text-gray-300">Uzatma</strong> 1.0&rsquo;a yakınsa spanner orijinale yakın.
        </p>
      </div>
    </aside>
  );
}
