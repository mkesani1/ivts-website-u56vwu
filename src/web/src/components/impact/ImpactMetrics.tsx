import React from 'react'; // react v18.2.0
import classNames from 'classnames'; // v2.3.2

import AnimatedCounter from '../shared/AnimatedCounter';
import Card from '../ui/Card';
import Icon from '../ui/Icon';
import { IMPACT_METRICS } from '../../constants/impact';
import { ImpactMetric } from '../../types/content';
import { Size, Variant } from '../../types/common';

/**
 * Props interface for the ImpactMetrics component
 */
interface ImpactMetricsProps extends React.HTMLAttributes<HTMLElement> {
  /** Optional array of custom impact metrics to display */
  metrics?: ImpactMetric[];
  /** Optional CSS class name */
  className?: string;
}

/**
 * Component that displays IndiVillage's key social impact metrics with animated counters
 */
const ImpactMetrics = ({
  metrics,
  className,
  ...props
}: ImpactMetricsProps): JSX.Element => {
  // Use provided metrics or default to IMPACT_METRICS constants
  const defaultMetrics = [
    IMPACT_METRICS.JOBS_CREATED,
    IMPACT_METRICS.COMMUNITIES_IMPACTED,
    IMPACT_METRICS.LIVES_TRANSFORMED,
    IMPACT_METRICS.WOMEN_EMPLOYED
  ];
  
  return (
    <section 
      className={classNames('impact-metrics', className)}
      aria-labelledby="impact-metrics-heading"
      {...props}
    >
      <h2 id="impact-metrics-heading" className="sr-only">Our Impact by the Numbers</h2>
      
      <div className="impact-metrics-grid">
        {metrics ? (
          // Render custom metrics from props
          metrics.map((metric) => {
            // Map to icon name based on metric ID
            let iconName = 'info' as const;
            if (metric.id === 'jobs_created') iconName = 'dataCollection';
            else if (metric.id === 'communities_impacted') iconName = 'dataPreparation';
            else if (metric.id === 'lives_transformed') iconName = 'aiModel';
            else if (metric.id === 'women_employed') iconName = 'humanInTheLoop';
            
            return (
              <Card
                key={metric.id}
                variant={Variant.PRIMARY}
                elevation={1}
                className="impact-metric-card"
                aria-labelledby={`metric-title-${metric.id}`}
              >
                <div className="impact-metric-icon" aria-hidden="true">
                  <Icon name={iconName} size={Size.LARGE} />
                </div>
                
                <div className="impact-metric-value">
                  <AnimatedCounter
                    value={parseFloat(metric.value)}
                    suffix={metric.unit}
                    duration={1500}
                    className="impact-metric-counter"
                    aria-label={`${metric.metric}: ${metric.value}${metric.unit}`}
                  />
                </div>
                
                <h3 id={`metric-title-${metric.id}`} className="impact-metric-title">{metric.metric}</h3>
                
                {metric.description && (
                  <p className="impact-metric-description">{metric.description}</p>
                )}
              </Card>
            );
          })
        ) : (
          // Render default metrics
          defaultMetrics.map((metric) => {
            // Map to icon name based on metric ID
            let iconName = 'info' as const;
            if (metric.id === 'jobs_created') iconName = 'dataCollection';
            else if (metric.id === 'communities_impacted') iconName = 'dataPreparation';
            else if (metric.id === 'lives_transformed') iconName = 'aiModel';
            else if (metric.id === 'women_employed') iconName = 'humanInTheLoop';
            
            return (
              <Card
                key={metric.id}
                variant={Variant.PRIMARY}
                elevation={1}
                className="impact-metric-card"
                aria-labelledby={`metric-title-${metric.id}`}
              >
                <div className="impact-metric-icon" aria-hidden="true">
                  <Icon name={iconName} size={Size.LARGE} />
                </div>
                
                <div className="impact-metric-value">
                  <AnimatedCounter
                    value={metric.value}
                    suffix={metric.suffix}
                    duration={1500}
                    className="impact-metric-counter"
                    aria-label={`${metric.title}: ${metric.value}${metric.suffix}`}
                  />
                </div>
                
                <h3 id={`metric-title-${metric.id}`} className="impact-metric-title">{metric.title}</h3>
                
                {metric.description && (
                  <p className="impact-metric-description">{metric.description}</p>
                )}
              </Card>
            );
          })
        )}
      </div>
    </section>
  );
};

export default ImpactMetrics;