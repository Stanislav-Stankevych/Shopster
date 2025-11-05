import NextAuth from "next-auth";

import { authOptions } from "@/lib/authOptions";

export const { handlers, auth, signIn, signOut } = NextAuth(authOptions);
