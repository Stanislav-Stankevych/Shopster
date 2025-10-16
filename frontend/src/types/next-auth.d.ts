import NextAuth, { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: {
      id: number;
      username: string;
      email: string;
      first_name: string;
      last_name: string;
      profile?: {
        phone?: string;
        avatar?: string | null;
        default_shipping_address?: string;
        default_shipping_city?: string;
        default_shipping_postcode?: string;
        default_shipping_country?: string;
      };
    } & DefaultSession["user"];
    accessToken?: string;
    error?: string;
  }

  interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    profile?: Session["user"]["profile"];
    accessToken: string;
    refreshToken: string;
    accessTokenExpires: number;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    user?: Session["user"];
    accessToken?: string;
    refreshToken?: string;
    accessTokenExpires?: number;
    error?: string;
  }
}
