'use client';

export default function RightSidebar() {
  return (
    <aside className="text-xs text-gray-500 leading-relaxed space-y-5">
      <div>
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
          Kullanim
        </h3>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 mb-1">Dosya Surukle</h4>
        <p>
          .conllu, .vrt, .csv veya .json dosyanizi surukleyin ya da
          &ldquo;Dosya Sec&rdquo; ile yukleyin. &ldquo;Ornek Veri ile Dene&rdquo;
          hazir bir derlemle aract kesfetmenizi saglar.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 mb-1">Gorunumler</h4>
        <ul className="space-y-1">
          <li><strong className="text-gray-700">Spanner</strong> &mdash; Orijinal ve seyreltilmis cizge</li>
          <li><strong className="text-gray-700">Trendler</strong> &mdash; Kliklerin zaman cizelgesi</li>
          <li><strong className="text-gray-700">Karsilastir</strong> &mdash; Iki donem yan yana</li>
          <li><strong className="text-gray-700">Kesfet</strong> &mdash; Kelime ve klik sorgulama</li>
        </ul>
      </div>

      <div className="pt-3 border-t border-gray-100">
        <h4 className="text-xs font-medium text-gray-600 mb-2">
          Dosya Sablonlari
        </h4>

        <div className="space-y-3">
          <div>
            <span className="text-[10px] font-semibold text-gray-600 uppercase">CoNLL-U</span>
            <pre className="mt-1 text-[10px] bg-gray-50 border border-gray-100 p-2 overflow-x-auto text-gray-600">
{`# date = 2020-01-15
1\tyapay\tyapay\tADJ
2\tzeka\tzeka\tNOUN
3\tveri\tveri\tNOUN

# date = 2020-06-10
1\tyapay\tyapay\tADJ
2\tdil\tdil\tNOUN`}
            </pre>
            <p className="mt-0.5 text-gray-400">Sutun 2 (FORM) veya 3 (LEMMA) okunur. <code># date =</code> satiri zamani belirler.</p>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-gray-600 uppercase">CSV</span>
            <pre className="mt-1 text-[10px] bg-gray-50 border border-gray-100 p-2 overflow-x-auto text-gray-600">
{`date,words
2020-01-15,"yapay,zeka,veri"
2020-06-10,"yapay,dil,isleme"`}
            </pre>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-gray-600 uppercase">JSON</span>
            <pre className="mt-1 text-[10px] bg-gray-50 border border-gray-100 p-2 overflow-x-auto text-gray-600">
{`[
  {"date":"2020-01-15","words":["yapay","zeka"]},
  {"date":"2020-06-10","words":["yapay","dil"]}
]`}
            </pre>
          </div>

          <div>
            <span className="text-[10px] font-semibold text-gray-600 uppercase">VRT</span>
            <pre className="mt-1 text-[10px] bg-gray-50 border border-gray-100 p-2 overflow-x-auto text-gray-600">
{`<text date="2020-01-15">
yapay\tADJ
zeka\tNOUN
veri\tNOUN
</text>`}
            </pre>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-gray-100">
        <h4 className="text-xs font-medium text-gray-600 mb-1">Yorumlama</h4>
        <p>
          <strong className="text-gray-700">Tasarruf %</strong> yuksekse iliskiler bagimli.{' '}
          <strong className="text-gray-700">Uzatma</strong> 1.0&rsquo;a yakinsa spanner orijinale yakin.
        </p>
      </div>
    </aside>
  );
}
