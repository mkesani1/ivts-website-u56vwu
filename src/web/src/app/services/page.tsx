import React from 'react';
import { Metadata } from 'next'; // version ^13.4.0

import PageHeader from '../../components/shared/PageHeader';
import SectionHeader from '../../components/shared/SectionHeader';
import ServiceCard from '../../components/services/ServiceCard';
import { getServices } from '../../services/contentService';
import { Service, ServiceCategory } from '../../types/content';
import { ROUTES } from '../../constants/routes';
import { SERVICE_CATEGORIES } from '../../constants/services';

/**
 * Generates static metadata for the services page
 * @returns Metadata object for the services page
 */
export const generateMetadata = (): Metadata => {
  return {
    title: 'AI-as-a-Service Solutions | IndiVillage',
    description: 'Explore IndiVillage\'s comprehensive AI-as-a-service offerings including data collection, data preparation, AI model development, and Human-in-the-Loop solutions.',
    keywords: [
      'AI services', 
      'data collection',
      'data preparation',
      'AI model development',
      'human-in-the-loop',
      'AI solutions',
      'social impact'
    ],
    openGraph: {
      title: 'AI-as-a-Service Solutions | IndiVillage',
      description: 'Explore IndiVillage\'s comprehensive AI-as-a-service offerings including data collection, data preparation, AI model development, and Human-in-the-Loop solutions.',
      images: [
        {
          url: '/images/og/services.jpg',
          width: 1200,
          height: 630,
          alt: 'IndiVillage AI Services'
        }
      ],
    },
  };
};

/**
 * Main services page component that displays all service categories
 * @returns Rendered services page component
 */
const ServicesPage = async (): Promise<JSX.Element> => {
  // Fetch all services
  const services = await getServices();

  // Define breadcrumbs for the page header
  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'Services', href: ROUTES.SERVICES.INDEX, current: true },
  ];

  return (
    <div className="services-page">
      <PageHeader 
        title="Our AI Services" 
        subtitle="Comprehensive AI solutions with positive social impact"
        breadcrumbs={breadcrumbs}
      />

      <div className="services-content">
        <section className="services-intro section">
          <div className="container">
            <div className="services-intro__content">
              <p className="services-intro__text">
                IndiVillage offers a comprehensive suite of AI-as-a-service solutions designed to help businesses transform their operations with cutting-edge technology while creating positive social impact.
              </p>
              <p className="services-intro__text">
                Our services span the entire AI lifecycle, from data collection and preparation to model development and human-in-the-loop solutions, all delivered by our talented team with a focus on quality and social responsibility.
              </p>
            </div>
          </div>
        </section>

        <section className="services-grid section section--alt">
          <div className="container">
            <SectionHeader 
              title="Explore Our Services" 
              subtitle="Find the right AI solution for your business needs"
            />
            
            <div className="services-grid__content">
              {Object.entries(SERVICE_CATEGORIES)
                .sort(([, a], [, b]) => a.order - b.order)
                .map(([category, details]) => {
                  const categoryServices = services.filter(
                    service => service.category === category
                  );
                  
                  // If we have a specific service for this category, use it, otherwise use the generic one
                  const serviceToRender = categoryServices.length > 0 ? 
                    categoryServices[0] : 
                    {
                      title: details.title,
                      description: details.description,
                      category: category,
                    };
                  
                  return (
                    <ServiceCard 
                      key={category}
                      service={serviceToRender}
                    />
                  );
              })}
            </div>
          </div>
        </section>

        <section className="service-benefits section">
          <div className="container">
            <SectionHeader 
              title="Why Choose IndiVillage's AI Services?" 
              subtitle="Creating business value with social impact"
            />
            
            <div className="service-benefits__grid">
              <div className="service-benefit">
                <h3 className="service-benefit__title">High-Quality AI Solutions</h3>
                <p className="service-benefit__description">Our expert team delivers exceptional AI services with rigorous quality assurance and attention to detail.</p>
              </div>
              
              <div className="service-benefit">
                <h3 className="service-benefit__title">Social Impact Integration</h3>
                <p className="service-benefit__description">Every project contributes to creating sustainable livelihoods and positive change in rural communities.</p>
              </div>
              
              <div className="service-benefit">
                <h3 className="service-benefit__title">End-to-End Capabilities</h3>
                <p className="service-benefit__description">Comprehensive services covering the entire AI lifecycle from data collection to model deployment.</p>
              </div>
              
              <div className="service-benefit">
                <h3 className="service-benefit__title">Scalable Resources</h3>
                <p className="service-benefit__description">Flexible team scaling to meet your project requirements, from small pilots to enterprise-scale implementations.</p>
              </div>
              
              <div className="service-benefit">
                <h3 className="service-benefit__title">Cost-Effective Solutions</h3>
                <p className="service-benefit__description">Efficient delivery models that provide exceptional value while maximizing social impact.</p>
              </div>
              
              <div className="service-benefit">
                <h3 className="service-benefit__title">Strategic Partnership</h3>
                <p className="service-benefit__description">Long-term collaboration focused on your success with dedicated support and continuous improvement.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="cta-section section section--primary">
          <div className="container">
            <SectionHeader 
              title="Ready to Transform Your Business?"
              subtitle="Get started with IndiVillage's AI services today"
              align="center"
            />
            
            <div className="cta-section__buttons">
              <a href={ROUTES.REQUEST_DEMO} className="btn btn--primary">
                Request Demo
              </a>
              <a href={ROUTES.UPLOAD_SAMPLE.INDEX} className="btn btn--secondary">
                Upload Sample Data
              </a>
              <a href={ROUTES.CONTACT} className="btn btn--tertiary">
                Contact Us
              </a>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ServicesPage;