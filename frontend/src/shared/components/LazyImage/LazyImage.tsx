import React, { useState, useRef, useEffect, useMemo } from 'react';
import { ImageOff } from 'lucide-react';

export interface LazyImageProps extends Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'sizes'> {
  src: string;
  alt: string;
  fallback?: string;
  placeholder?: string;
  className?: string;
  onError?: () => void;
  /**
   * Enable WebP format support (automatically detects browser support)
   */
  enableWebP?: boolean;
  /**
   * Responsive image sizes for srcset
   * Format: ['400w', '800w', '1200w'] or ['1x', '2x', '3x']
   */
  srcsetSizes?: string[];
  /**
   * Sizes attribute for responsive images
   * Example: '(max-width: 768px) 100vw, 50vw'
   */
  sizes?: string;
}

/**
 * Check if browser supports WebP format
 */
const supportsWebP = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
};

/**
 * Generate WebP version of image URL if supported
 */
const getWebPSrc = (src: string, enableWebP: boolean): string => {
  if (!enableWebP || !supportsWebP()) return src;
  
  // If URL already has format parameter, replace it
  if (src.includes('format=')) {
    return src.replace(/format=\w+/, 'format=webp');
  }
  
  // If URL has query parameters, append format
  if (src.includes('?')) {
    return `${src}&format=webp`;
  }
  
  // Otherwise, add format parameter
  return `${src}?format=webp`;
};

/**
 * Generate srcset for responsive images
 */
const generateSrcSet = (src: string, sizes: string[], enableWebP: boolean): string => {
  if (!sizes || sizes.length === 0) return '';
  
  const webPSrc = enableWebP ? getWebPSrc(src, true) : src;
  const baseSrc = enableWebP ? src : src;
  
  return sizes
    .map((size) => {
      const isWidth = size.endsWith('w');
      const isDensity = size.endsWith('x');
      
      if (isWidth) {
        // Width-based: ?w=400 400w
        const width = size.replace('w', '');
        const webPUrl = webPSrc.includes('?') 
          ? `${webPSrc}&w=${width}` 
          : `${webPSrc}?w=${width}`;
        const fallbackUrl = baseSrc.includes('?') 
          ? `${baseSrc}&w=${width}` 
          : `${baseSrc}?w=${width}`;
        return supportsWebP() && enableWebP 
          ? `${webPUrl} ${size}` 
          : `${fallbackUrl} ${size}`;
      } else if (isDensity) {
        // Density-based: ?dpr=2 2x
        const density = size.replace('x', '');
        const webPUrl = webPSrc.includes('?') 
          ? `${webPSrc}&dpr=${density}` 
          : `${webPSrc}?dpr=${density}`;
        const fallbackUrl = baseSrc.includes('?') 
          ? `${baseSrc}&dpr=${density}` 
          : `${baseSrc}?dpr=${density}`;
        return supportsWebP() && enableWebP 
          ? `${webPUrl} ${size}` 
          : `${fallbackUrl} ${size}`;
      }
      return '';
    })
    .filter(Boolean)
    .join(', ');
};

/**
 * Lazy-loaded image component with IntersectionObserver
 * Supports WebP format, responsive images, and automatic lazy loading
 */
export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  fallback,
  placeholder,
  className = '',
  onError,
  enableWebP = true,
  srcsetSizes,
  sizes,
  ...props
}) => {
  const [imageSrc, setImageSrc] = useState<string | null>(placeholder || null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [webPSupported, setWebPSupported] = useState<boolean | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  // Check WebP support once on mount
  useEffect(() => {
    if (enableWebP) {
      setWebPSupported(supportsWebP());
    }
  }, [enableWebP]);

  // Generate optimized image source
  const optimizedSrc = useMemo(() => {
    if (!imageSrc || imageSrc === placeholder) return imageSrc;
    return enableWebP && webPSupported ? getWebPSrc(imageSrc, true) : imageSrc;
  }, [imageSrc, enableWebP, webPSupported, placeholder]);

  // Generate srcset if sizes provided
  const srcSet = useMemo(() => {
    if (!srcsetSizes || srcsetSizes.length === 0 || !imageSrc || imageSrc === placeholder) return undefined;
    return generateSrcSet(imageSrc, srcsetSizes, enableWebP);
  }, [imageSrc, srcsetSizes, enableWebP, placeholder]);

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    // If browser doesn't support IntersectionObserver, load immediately
    if (!('IntersectionObserver' in window)) {
      setImageSrc(src);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '100px', // Start loading 100px before entering viewport
      }
    );

    observer.observe(img);

    return () => {
      observer.disconnect();
    };
  }, [src]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    if (fallback) {
      setImageSrc(fallback);
      setHasError(false);
    }
    onError?.();
  };

  if (hasError && !fallback) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-100 ${className}`}
        {...props}
      >
        <ImageOff className="h-8 w-8 text-gray-400" />
      </div>
    );
  }

  return (
    <img
      ref={imgRef}
      src={optimizedSrc || undefined}
      srcSet={srcSet}
      sizes={sizes}
      alt={alt}
      className={`${className} ${!isLoaded ? 'opacity-0' : 'opacity-100 transition-opacity duration-300'}`}
      onLoad={handleLoad}
      onError={handleError}
      loading="lazy"
      decoding="async"
      {...props}
    />
  );
};

