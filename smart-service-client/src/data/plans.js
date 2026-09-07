export const companyPlans = [
  {
    id: "company_basic",
    name: "Company Basic",
    duration: "1 month",
    priority: 3,
    price: 99,
    description: "For small companies with a low number of support requests.",
  },
  {
    id: "company_pro",
    name: "Company Pro",
    duration: "6 months",
    priority: 2,
    price: 499,
    description: "For companies with a medium number of support requests.",
  },
  {
    id: "company_premium",
    name: "Company Premium",
    duration: "1 year",
    priority: 1,
    price: 899,
    description: "High priority, extended service, and advanced management.",
  },
];

export const customerPlans = [
  {
    id: "customer_symbolic",
    name: "Customer Basic",
    duration: "1 month",
    priority: 3,
    price: 5,
    description: "A symbolic payment for basic system usage.",
  },
  {
    id: "customer_plus",
    name: "Customer Plus",
    duration: "3 months",
    priority: 2,
    price: 12,
    description: "Better access with extended conversation history.",
  },
];

export const adminDefaultPlans = [
  ...companyPlans,
  ...customerPlans,
];