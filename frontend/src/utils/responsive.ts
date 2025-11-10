// Responsive breakpoints
export const BREAKPOINTS = {
  mobile: 767,
  tablet: 1023,
  desktop: 1024,
} as const;

// Media query hooks helper
export const getMediaQuery = (breakpoint: keyof typeof BREAKPOINTS, direction: 'max' | 'min' = 'max') => {
  const value = BREAKPOINTS[breakpoint];
  return `(${direction}-width: ${value}px)`;
};

