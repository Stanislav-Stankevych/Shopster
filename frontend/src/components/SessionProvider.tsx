"use client";

import { SessionProvider } from "next-auth/react";
import { PropsWithChildren } from "react";

export function AuthSessionProvider({ children }: PropsWithChildren) {
  return <SessionProvider>{children}</SessionProvider>;
}
