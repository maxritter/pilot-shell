import { useState, useEffect, useCallback } from 'react';
import type { LicenseResponse } from '../../../services/worker/http/routes/LicenseRoutes.js';

interface UseLicenseResult {
  license: LicenseResponse | null;
  isLoading: boolean;
  refetch: () => void;
}

export function useLicense(): UseLicenseResult {
  const [license, setLicense] = useState<LicenseResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchLicense = useCallback((refresh = false) => {
    const url = refresh ? '/api/license?refresh=1' : '/api/license';
    fetch(url)
      .then((res) => res.json())
      .then((data: LicenseResponse) => {
        setLicense(data);
        setIsLoading(false);
      })
      .catch(() => {
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    fetchLicense();
    const interval = setInterval(() => fetchLicense(true), 60_000);
    return () => clearInterval(interval);
  }, [fetchLicense]);

  const refetch = useCallback(() => fetchLicense(true), [fetchLicense]);

  return { license, isLoading, refetch };
}
