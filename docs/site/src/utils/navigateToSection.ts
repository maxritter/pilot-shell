import { NavigateFunction } from 'react-router-dom';

const SECTION_RETRY_DELAY_MS = 50;
const SECTION_RETRY_LIMIT = 100;

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

/** Wait briefly for a lazily loaded homepage section, then scroll once it mounts. */
const scrollAndFocusWhenAvailable = (sectionId: string, attempt = 0): void => {
  if (scrollAndFocusSection(sectionId) || attempt >= SECTION_RETRY_LIMIT) return;
  window.setTimeout(
    () => scrollAndFocusWhenAvailable(sectionId, attempt + 1),
    SECTION_RETRY_DELAY_MS,
  );
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
    scrollAndFocusWhenAvailable(id);
  } else {
    navigate(`/#${id}`);
  }
};
