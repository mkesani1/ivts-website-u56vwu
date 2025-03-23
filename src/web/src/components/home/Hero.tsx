import React from 'react'; // version 18.2.0
import Image from 'next/image'; // version 13.4.0
import Link from 'next/link'; // version 13.4.0
import classNames from 'classnames'; // version 2.3.2

import Button from '../../components/ui/Button';
import Icon from '../../components/ui/Icon';
import { ROUTES } from '../../constants/routes';
import { useFadeIn, useSlideIn } from '../../utils/animations';

/**
 * Hero component for the IndiVillage homepage
 * 
 * Displays a visually striking banner with headline, subheading, and CTAs that introduce
 * visitors to IndiVillage's AI-powered solutions and social impact mission.
 */
const Hero: React.FC = () => {
  // Animation hooks for content elements
  const headlineAnimation = useFadeIn({ 
    duration: 600, 
    delay: 100,
    translateY: 20 
  });
  
  const subheadingAnimation = useFadeIn({ 
    duration: 600, 
    delay: 300,
    translateY: 20 
  });
  
  const ctaAnimation = useSlideIn('bottom', { 
    duration: 600, 
    delay: 500,
    distance: 30 
  });

  return (
    <section className="relative w-full overflow-hidden bg-gradient-to-r from-gray-900 to-blue-900 text-white">
      {/* Background image with overlay */}
      <div className="absolute inset-0 z-0">
        <Image
          src="/images/hero-background.jpg"
          alt="Digital AI visualization"
          fill
          priority
          className="object-cover opacity-20"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-primary-900/80 to-transparent"></div>
      </div>

      {/* Hero content container */}
      <div className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 lg:py-32">
        <div className="max-w-3xl">
          {/* Main headline */}
          <h1 
            className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6"
            ref={headlineAnimation.ref}
            style={headlineAnimation.style}
          >
            AI-Powered Solutions <span className="text-secondary-400">with Social Impact</span>
          </h1>
          
          {/* Subheading */}
          <p 
            className="text-xl md:text-2xl mb-8 text-gray-100 max-w-2xl"
            ref={subheadingAnimation.ref}
            style={subheadingAnimation.style}
          >
            Transform your business with AI solutions that create positive social change. 
            Our cutting-edge technology delivers exceptional results while empowering 
            communities.
          </p>
          
          {/* Call-to-action buttons */}
          <div 
            className="flex flex-col sm:flex-row gap-4"
            ref={ctaAnimation.ref}
            style={ctaAnimation.style}
          >
            <Link href={ROUTES.SERVICES.INDEX}>
              <Button 
                variant="secondary" 
                size="large"
                className="w-full sm:w-auto"
              >
                Learn More
              </Button>
            </Link>
            
            <Link href={ROUTES.REQUEST_DEMO}>
              <Button 
                variant="primary" 
                size="large" 
                icon="arrowRight" 
                iconPosition="right"
                className="w-full sm:w-auto"
              >
                Request Demo
              </Button>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Decorative elements */}
      <div className="absolute bottom-0 right-0 w-1/3 h-16 md:h-24 bg-secondary-500 transform translate-x-1/2 rotate-3 z-0 opacity-80"></div>
      <div className="absolute bottom-10 right-10 hidden lg:block">
        <Icon 
          name="dataCollection" 
          size={80} 
          className="text-primary-300/30" 
        />
      </div>
    </section>
  );
};

export default Hero;