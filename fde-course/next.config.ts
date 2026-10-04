import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Lesson markdown and exercise files are read from disk at request time.
  outputFileTracingIncludes: {
    "/learn/[module]/[lesson]": ["./content/**/*"],
    "/learn": ["./content/**/*"],
    "/": ["./content/**/*"],
  },
};

export default nextConfig;
