import React from 'react'; // version 18.2.0
import classNames from 'classnames'; // version 2.3.2
import { motion } from 'framer-motion'; // version 10.12.0

import Card from '../ui/Card';
import Icon from '../ui/Icon';
import SectionHeader from '../shared/SectionHeader';
import { IconName } from '../../types/common';

// Interface for step data structure
export interface Step {
  title: string;
  description: string;
  icon?: string;
}

// Interface for HowItWorks component props
export interface HowItWorksProps {
  steps: Step[];
  className?: string;
}

/**
 * Helper function to get the appropriate icon for a step based on its index or custom icon
 */
const getStepIcon = (step: Step, index: number): IconName => {
  // If step has a custom icon, return it
  if (step.icon) {
    return step.icon as IconName;
  }
  
  // Otherwise, return a default icon based on step index
  switch (index) {
    case 0:
      return 'dataCollection'; // Data Receipt
    case 1:
      return 'dataPreparation'; // Expert Process
    case 2:
      return 'check'; // Quality Check
    case 3:
      return 'arrowRight'; // Delivery & Report
    default:
      return 'arrowRight';
  }
};

/**
 * Component that displays a step-by-step visualization of how a service works
 */
const HowItWorks: React.FC<HowItWorksProps> = ({ steps, className }) => {
  // Animation variants for step cards
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.2,
        duration: 0.5,
        ease: "easeOut"
      }
    })
  };

  return (
    <section className={classNames('how-it-works', className)}>
      <SectionHeader title="How It Works" />
      
      <div className="how-it-works__steps">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            custom={index}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={cardVariants}
            className="how-it-works__step"
          >
            <Card className="how-it-works__card">
              <div className="how-it-works__step-number">{index + 1}</div>
              <div className="how-it-works__step-icon">
                <Icon name={getStepIcon(step, index)} />
              </div>
              <h4 className="how-it-works__step-title">{step.title}</h4>
              <p className="how-it-works__step-description">{step.description}</p>
            </Card>
            
            {/* Add connecting lines between steps (except for the last step) */}
            {index < steps.length - 1 && (
              <div className="how-it-works__connector" aria-hidden="true" />
            )}
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default HowItWorks;