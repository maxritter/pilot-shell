import { NavigateFunction } from 'react-router-dom';

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
    const element = document.querySelector(`#${CSS.escape(id)}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  } else {
    navigate(`/#${id}`);
  }
};
