import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { scrollAndFocusSection } from '@/utils/navigateToSection';

/**
 * Handles scrolling to hash fragments after cross-page navigation.
 * Uses retry pattern to wait for target element to be in the DOM.
 */
const ScrollToHash = () => {
  const { hash, pathname } = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!hash) return;

    const id = hash.slice(1);

    if (id === 'pricing' && pathname !== '/pricing' && !document.querySelector('#pricing')) {
      navigate('/pricing', { replace: true });
      return;
    }

    const scrollToElement = () => {
      const element = document.querySelector(`#${CSS.escape(id)}`);
      if (element) {
        requestAnimationFrame(() => {
          scrollAndFocusSection(id);
        });
        return true;
      }
      return false;
    };

    if (scrollToElement()) return;

    const timeouts: Array<ReturnType<typeof setTimeout>> = [];
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
  }, [hash, pathname, navigate]);

  return null;
};

export default ScrollToHash;
