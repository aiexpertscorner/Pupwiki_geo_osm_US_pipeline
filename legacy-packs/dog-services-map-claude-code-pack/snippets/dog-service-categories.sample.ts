// Sample shape for src/features/dog-services/data/dogServiceCategories.ts

export const DOG_SERVICE_CATEGORIES = [
  {
    id: "veterinary_clinics",
    slug: "veterinary-clinics",
    label: "Veterinary Clinics",
    shortLabel: "Vets",
    tier: "core",
    iconName: "stethoscope",
    markerClass: "vet",
    description: "Veterinary clinics and animal hospitals.",
    osmTags: [{ key: "amenity", value: "veterinary" }],
    optionalTags: [],
    dataQuality: "high",
    seoPathTemplate: "/dog-services/{state}/{city}/veterinarians/",
    disclaimerType: "veterinary"
  },
  {
    id: "emergency_vets",
    slug: "emergency-vets",
    label: "Emergency Vets",
    shortLabel: "Emergency",
    tier: "core",
    iconName: "siren",
    markerClass: "emergency-vet",
    description: "Veterinary clinics with emergency availability.",
    osmTags: [
      { key: "amenity", value: "veterinary" },
      { key: "emergency", value: "yes" }
    ],
    optionalTags: [],
    dataQuality: "medium",
    seoPathTemplate: "/dog-services/{state}/{city}/emergency-vets/",
    disclaimerType: "emergency"
  }
] as const;
