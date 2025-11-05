import { AccountProfileForm } from "@/components/AccountProfileForm";
import { API_BASE_URL } from "@/lib/config";
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

type ProfilePayload = {
  first_name?: string;
  last_name?: string;
  profile?: {
    phone?: string;
    default_shipping_address?: string;
    default_shipping_city?: string;
    default_shipping_postcode?: string;
    default_shipping_country?: string;
  };
};

async function fetchProfile(accessToken: string): Promise<ProfilePayload> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me/`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load profile");
  }

  return response.json();
}

export default async function AccountPage() {
  const session = await auth();

  if (!session?.accessToken) {
    redirect("/signin");
  }

  try {
    const profile = await fetchProfile(session.accessToken as string);

    return (
      <section className="section">
        <div className="container auth-card">
          <h1>Account</h1>
          <p className="auth-subtitle">
            Update personal details and your default shipping address.
          </p>
          <AccountProfileForm initialData={profile} />
        </div>
      </section>
    );
  } catch (error) {
    console.error(error);
    redirect("/signin");
  }
}
