import React from "react";

type Props = {
  children?: React.ReactNode;
};

export default function AnimatedBackground({ children }: Props) {
  return (
    <div
      className="relative min-h-screen flex flex-col items-center justify-center
                    bg-gradient-to-br from-black via-gray-900 to-gray-800
                    text-white"
    >
      {children}
    </div>
  );
}
