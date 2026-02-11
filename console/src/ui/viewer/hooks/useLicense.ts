import { useState, useEffect } from 'react';
import type { LicenseResponse } from '../../../services/worker/http/routes/LicenseRoutes.js';

interface UseLicenseResult {
  license: LicenseResponse | null;
  isLoading: boolean;
}

export function useLicense(): UseLicenseResult {
  const [license, setLicense] = useState<LicenseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('/api/license')
      .then((res) => res.json())
      .then((data: LicenseResponse) => {
        setLicense(data);
        setIsLoading(false);
      })
      .catch(() => {
        setIsLoading(false);
      });
  }, []);

  return { license, isLoading };
}
