import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Lesson markdown and exercise files are read from disk at request time.
  outputFileTracingIncludes: {
    "/learn/[module]/[lesson]": ["./content/**/*"],
    "/learn": ["./content/**/*"],
    "/": ["./content/**/*"],
  },
  // These pages live at the top level; send typed guesses under /learn to the right place.
  async redirects() {
    return ["review", "start", "community"].map((page) => ({
      source: `/learn/${page}`,
      destination: `/${page}`,
      permanent: false,
    }));
  },
};

export default nextConfig;
