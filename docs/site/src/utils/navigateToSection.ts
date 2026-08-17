import { NavigateFunction } from 'react-router-dom';

function preferredScrollBehavior(): ScrollBehavior {
  if (
    typeof window !== 'undefined' &&
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  ) {
    return 'auto';
  }
  return 'smooth';
}

/** Scroll to a section and move keyboard focus with the viewport. */
export const scrollAndFocusSection = (sectionId: string): boolean => {
  const id = sectionId.startsWith('#') ? sectionId.slice(1) : sectionId;
  const element = document.querySelector<HTMLElement>(`#${CSS.escape(id)}`);
  if (!element) return false;

  element.scrollIntoView({ behavior: preferredScrollBehavior() });
  if (!element.hasAttribute('tabindex')) {
    element.setAttribute('tabindex', '-1');
  }
  element.focus({ preventScroll: true });
  return true;
};

/**
 * Shared navigation helper for cross-page section navigation.
 * - On homepage: scrolls to the section
 * - On other pages: navigates to homepage with hash
 */
export const navigateToSection = (
  sectionId: string,
  currentPath: string,
  navigate: NavigateFunction
): void => {
  const id = sectionId.startsWith('#') ? sectionId.slice(1) : sectionId;

  if (currentPath === '/') {
    scrollAndFocusSection(id);
  } else {
    navigate(`/#${id}`);
  }
};
