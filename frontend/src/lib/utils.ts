export function formatCurrency(currency: string, amount: number): string {
  const formatter = new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: currency || "RUB",
  });
  return formatter.format(amount);
}
