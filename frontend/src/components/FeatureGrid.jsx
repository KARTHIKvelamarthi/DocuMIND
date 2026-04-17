import '../styles/FeatureGrid.css';

const FEATURES = [
  {
    icon: '📄',
    title: 'Multi-PDF Comparison',
    desc: 'Upload two documents and get side-by-side AI analysis.',
  },
  {
    icon: '🧠',
    title: 'Context-Aware Memory',
    desc: 'Follow-up questions build on previous answers automatically.',
  },
  {
    icon: '🔍',
    title: 'Structured Retrieval',
    desc: 'Hybrid BM25 + semantic search with cross-encoder reranking.',
  },
  {
    icon: '🖼️',
    title: 'Visual Extraction',
    desc: 'Images and tables are extracted and linked to relevant chunks.',
  },
];

export default function FeatureGrid() {
  return (
    <div className="feature-grid-wrapper">
      <h1 className="hero-title">DocuMind</h1>
      <p className="hero-sub">Your AI-powered document intelligence system</p>
      <div className="feature-grid">
        {FEATURES.map((f) => (
          <div key={f.title} className="feature-card">
            <span className="feature-icon">{f.icon}</span>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
