import React from 'react';

export const DecorativeBlobs: React.FC = () => {
  return (
    <>
      {/* Blob 1 - Top Left */}
      <svg
        className="absolute -left-20 -top-20 h-96 w-96 opacity-30 animate-float-slow"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="blob1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#FF6B35', stopOpacity: 0.3 }} />
            <stop offset="100%" style={{ stopColor: '#004E89', stopOpacity: 0.2 }} />
          </linearGradient>
        </defs>
        <path
          fill="url(#blob1)"
          d="M44.7,-76.4C58.8,-69.2,71.8,-59.1,79.6,-45.8C87.4,-32.6,90,-16.3,88.5,-0.9C87,14.6,81.4,29.2,73.1,42.3C64.8,55.4,53.8,67,40.4,73.8C27,80.6,11.2,82.6,-4.5,89.7C-20.2,96.8,-35.8,109,-48.7,107.8C-61.6,106.6,-71.8,92,-78.4,76.1C-85,60.2,-88,43,-86.8,26.8C-85.6,10.6,-80.2,-4.6,-73.4,-18.4C-66.6,-32.2,-58.4,-44.6,-47.8,-53.2C-37.2,-61.8,-24.2,-66.6,-10.6,-69.8C3,-73,18.6,-74.6,32.9,-72.9C47.2,-71.2,60.2,-66.2,44.7,-76.4Z"
          transform="translate(100 100)"
        />
      </svg>

      {/* Blob 2 - Top Right */}
      <svg
        className="absolute -right-32 -top-32 h-[500px] w-[500px] opacity-20 animate-float-slow-reverse"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="blob2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#004E89', stopOpacity: 0.3 }} />
            <stop offset="100%" style={{ stopColor: '#28A745', stopOpacity: 0.2 }} />
          </linearGradient>
        </defs>
        <path
          fill="url(#blob2)"
          d="M37.1,-63.3C48.9,-56.9,59.7,-47.9,67.3,-36.2C74.9,-24.5,79.3,-10.1,79.5,4.5C79.7,19.1,75.7,33.9,67.9,46.2C60.1,58.5,48.5,68.3,35.3,74.8C22.1,81.3,7.3,84.5,-7.2,84.1C-21.7,83.7,-36,79.7,-48.3,71.9C-60.6,64.1,-71,52.5,-77.2,38.9C-83.4,25.3,-85.4,9.7,-83.3,-4.9C-81.2,-19.5,-75,-33.1,-65.8,-44.2C-56.6,-55.3,-44.4,-63.9,-31.5,-69.5C-18.6,-75.1,-5,-77.7,6.7,-77.2C18.4,-76.7,25.3,-69.7,37.1,-63.3Z"
          transform="translate(100 100)"
        />
      </svg>

      {/* Blob 3 - Bottom Left */}
      <svg
        className="absolute -bottom-20 -left-32 h-96 w-96 opacity-25 animate-float"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="blob3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#FFC107', stopOpacity: 0.3 }} />
            <stop offset="100%" style={{ stopColor: '#FF6B35', stopOpacity: 0.2 }} />
          </linearGradient>
        </defs>
        <path
          fill="url(#blob3)"
          d="M41.3,-71.8C53.4,-64.3,62.7,-53.3,69.8,-40.8C76.9,-28.3,81.8,-14.2,82.2,0.3C82.6,14.8,78.5,29.6,70.8,42.7C63.1,55.8,51.8,67.2,38.2,74.3C24.6,81.4,8.7,84.2,-6.6,83.3C-21.9,82.4,-36.6,77.8,-49.5,69.7C-62.4,61.6,-73.5,50,-78.9,36.4C-84.3,22.8,-84,7.2,-80.2,-7.1C-76.4,-21.4,-69.1,-34.4,-59.1,-45.1C-49.1,-55.8,-36.4,-64.2,-23.1,-71.1C-9.8,-78,-4.9,-83.4,3.9,-85.3C12.7,-87.2,29.2,-79.3,41.3,-71.8Z"
          transform="translate(100 100)"
        />
      </svg>
    </>
  );
};

