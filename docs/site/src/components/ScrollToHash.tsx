import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Handles scrolling to hash fragments after cross-page navigation.
 * Uses retry pattern to wait for target element to be in the DOM.
 */
const ScrollToHash = () => {
  const { hash } = useLocation();

  useEffect(() => {
    if (!hash) return;

    const id = hash.slice(1);

    const scrollToElement = () => {
      const element = document.querySelector(`#${CSS.escape(id)}`);
      if (element) {
        requestAnimationFrame(() => {
          element.scrollIntoView({ behavior: 'smooth' });
        });
        return true;
      }
      return false;
    };

    if (scrollToElement()) return;

    const timeouts: NodeJS.Timeout[] = [];
    const delays = [50, 100, 200, 300, 350];

    delays.forEach((delay) => {
      const timeout = setTimeout(() => {
        if (scrollToElement()) {
          timeouts.forEach(clearTimeout);
        }
      }, delay);
      timeouts.push(timeout);
    });

    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, [hash]);

  return null;
};

export default ScrollToHash;
