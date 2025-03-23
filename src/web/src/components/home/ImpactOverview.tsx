import React, { useState, useEffect } from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import Image from 'next/image'; // version 13.4.0
import Link from 'next/link'; // version 13.4.0

import SectionHeader from '../shared/SectionHeader';
import AnimatedCounter from '../shared/AnimatedCounter';
import Button from '../ui/Button';
import Card from '../ui/Card';
import { IMPACT_METRICS } from '../../constants/impact';
import { ROUTES } from '../../constants/routes';
import useIntersectionObserver from '../../hooks/useIntersectionObserver';

/**
 * Props interface for the ImpactOverview component
 */
interface ImpactOverviewProps extends React.HTMLAttributes<HTMLElement> {
  /**
   * Additional CSS class names
   */
  className?: string;
}

/**
 * Props interface for the internal ImpactMetricCard component
 */
interface ImpactMetricCardProps {
  /**
   * Impact metric data object
   */
  metric: typeof IMPACT_METRICS.JOBS_CREATED;
  /**
   * Additional CSS class names
   */
  className?: string;
  /**
   * Whether the animation should be triggered
   */
  animate: boolean;
  /**
   * Animation delay in milliseconds
   */
  animationDelay?: number;
}

/**
 * Component that displays IndiVillage's social impact metrics and mission statement on the homepage.
 * Features animated counters for key impact statistics, a brief mission description, and a
 * call-to-action to learn more about the foundation.
 */
const ImpactOverview: React.FC<ImpactOverviewProps> = ({ className, ...rest }) => {
  // Use the intersection observer hook to detect when the section is visible
  const [sectionRef, isVisible] = useIntersectionObserver<HTMLElement>({
    threshold: 0.1, // Trigger when at least 10% of the section is visible
  });

  // State to track if animations have been triggered
  const [animationTriggered, setAnimationTriggered] = useState(false);

  // Trigger animations once when the section becomes visible
  useEffect(() => {
    if (isVisible && !animationTriggered) {
      setAnimationTriggered(true);
    }
  }, [isVisible, animationTriggered]);

  // Extract the impact metrics from the constants
  const { JOBS_CREATED, COMMUNITIES_IMPACTED, LIVES_TRANSFORMED, WOMEN_EMPLOYED } = IMPACT_METRICS;

  // Generate CSS classes for the component
  const sectionClasses = classNames('impact-overview', className);

  return (
    <section 
      ref={sectionRef}
      className={sectionClasses}
      {...rest}
    >
      <div className="container">
        <SectionHeader 
          title="AI FOR GOOD: OUR IMPACT"
          align="center"
          headingLevel="h2"
          className="impact-overview__header"
        />
        
        <div className="impact-overview__metrics">
          <ImpactMetricCard 
            metric={JOBS_CREATED} 
            animate={animationTriggered}
            animationDelay={0}
          />
          <ImpactMetricCard 
            metric={COMMUNITIES_IMPACTED} 
            animate={animationTriggered}
            animationDelay={200}
          />
          <ImpactMetricCard 
            metric={LIVES_TRANSFORMED} 
            animate={animationTriggered}
            animationDelay={400}
          />
          <ImpactMetricCard 
            metric={WOMEN_EMPLOYED} 
            animate={animationTriggered}
            animationDelay={600}
          />
        </div>
        
        <div className="impact-overview__mission">
          <div className={classNames(
            'impact-overview__mission-image',
            { 'impact-overview__mission-image--animate': animationTriggered }
          )}>
            <Image 
              src="/images/impact/community-impact.jpg"
              alt="IndiVillage community impact initiatives"
              width={560}
              height={400}
              quality={90}
            />
          </div>
          <Card 
            className={classNames(
              'impact-overview__mission-content',
              { 'impact-overview__mission-content--animate': animationTriggered }
            )}
            elevation={2}
          >
            <h3 className="impact-overview__mission-title">OUR MISSION</h3>
            <p className="impact-overview__mission-text">
              Creating sustainable livelihoods through technology while delivering exceptional 
              AI services to global clients. Our unique "AI for Good" model combines technical 
              excellence with positive social change in rural communities.
            </p>
            <Link href={ROUTES.IMPACT.FOUNDATION} passHref>
              <Button variant="secondary" icon="arrowRight" iconPosition="right">
                Learn About Our Foundation
              </Button>
            </Link>
          </Card>
        </div>
      </div>
    </section>
  );
};

/**
 * Component that displays a single impact metric with an animated counter
 */
const ImpactMetricCard: React.FC<ImpactMetricCardProps> = ({ 
  metric, 
  className, 
  animate, 
  animationDelay = 0 
}) => {
  return (
    <Card 
      className={classNames('impact-metric-card', className, {
        'impact-metric-card--animate': animate
      })}
      elevation={1}
      style={animate ? { transitionDelay: `${animationDelay}ms` } : undefined}
    >
      <div className="impact-metric-card__value">
        <AnimatedCounter 
          value={metric.value} 
          suffix={metric.suffix}
          className="impact-metric-card__counter"
          delay={animate ? animationDelay : 0}
          duration={1200}
        />
      </div>
      <h3 className="impact-metric-card__title">{metric.title}</h3>
      <p className="impact-metric-card__description">{metric.description}</p>
    </Card>
  );
};

export default ImpactOverview;