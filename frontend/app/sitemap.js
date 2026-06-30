export default function sitemap() {
  const baseUrl = "https://frontend-teal-iota-ee3dg8j6wx.vercel.app";

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 1,
    },
  ];
}
