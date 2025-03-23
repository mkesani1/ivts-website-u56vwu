import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';

import PageHeader from '../../../components/shared/PageHeader';
import SectionHeader from '../../../components/shared/SectionHeader';
import Card from '../../../components/ui/Card';
import ImageWithFallback from '../../../components/shared/ImageWithFallback';
import { generateMetadata as generateMetaData } from '../../../utils/seo';
import { getTeamMembers } from '../../../services/contentService';
import { ROUTES } from '../../../constants/routes';
import { TeamMember } from '../../../types/content';

// A constant for the introduction text
const LEADERSHIP_INTRO = "Our leadership team brings together expertise in AI technology and social impact to drive IndiVillage's mission of providing cutting-edge AI services while creating sustainable livelihoods in rural communities.";

/**
 * Generate metadata for the leadership page using Next.js App Router metadata API
 */
export const generateMetadata = (): Metadata => {
  return generateMetaData({
    title: 'Leadership Team',
    description: "Meet the leadership team behind IndiVillage's AI-powered solutions with social impact",
    keywords: ['leadership', 'team', 'AI experts', 'social impact', 'executive team', 'IndiVillage leadership'],
    section: 'About Us'
  });
};

/**
 * Leadership page component that displays the executive team of IndiVillage
 */
export default async function LeadershipPage(): Promise<JSX.Element> {
  // Fetch team members with leadership role
  const teamMembers = await getTeamMembers({
    'fields.role': 'leadership'
  });
  
  // Sort team members by their order property to display in correct hierarchy
  const sortedTeamMembers = teamMembers.sort((a, b) => a.order - b.order);

  return (
    <main className="page page--leadership">
      {/* Page header with breadcrumbs */}
      <PageHeader 
        title="Leadership Team" 
        breadcrumbs={[
          { label: 'Home', href: ROUTES.HOME },
          { label: 'About Us', href: ROUTES.ABOUT.INDEX },
          { label: 'Leadership Team', href: ROUTES.ABOUT.LEADERSHIP, current: true }
        ]}
      />
      
      {/* Introduction section */}
      <section className="section section--intro">
        <div className="container">
          <p className="section__text section__text--centered">
            {LEADERSHIP_INTRO}
          </p>
        </div>
      </section>
      
      {/* Team members grid section */}
      <section className="section section--team">
        <div className="container">
          <SectionHeader title="Executive Team" />
          
          {sortedTeamMembers.length === 0 ? (
            <p className="section__text section__text--centered section__text--empty">
              Leadership team information is currently being updated.
            </p>
          ) : (
            <div className="team-grid">
              {sortedTeamMembers.map((member) => (
                <Card 
                  key={member.id} 
                  className="team-member-card"
                  elevation={2}
                  hoverable
                >
                  <div className="team-member-card__photo">
                    <ImageWithFallback 
                      src={member.photo?.url || ''} 
                      alt={`${member.name} - ${member.title}`}
                      width={400}
                      height={400}
                      className="team-member-card__image"
                      objectFit="cover"
                    />
                  </div>
                  
                  <div className="team-member-card__content">
                    <h3 className="team-member-card__name">{member.name}</h3>
                    <p className="team-member-card__title">{member.title}</p>
                    
                    <div className="team-member-card__bio">
                      <p>{member.bio}</p>
                    </div>
                    
                    {/* Social media links if available */}
                    {member.socialLinks && Object.keys(member.socialLinks).length > 0 && (
                      <div className="team-member-card__social">
                        {member.socialLinks.linkedin && (
                          <Link 
                            href={member.socialLinks.linkedin}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="team-member-card__social-link"
                            aria-label={`${member.name} LinkedIn profile`}
                          >
                            <Icon name="linkedin" />
                          </Link>
                        )}
                        {member.socialLinks.twitter && (
                          <Link 
                            href={member.socialLinks.twitter}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="team-member-card__social-link"
                            aria-label={`${member.name} Twitter profile`}
                          >
                            <Icon name="twitter" />
                          </Link>
                        )}
                        {member.socialLinks.facebook && (
                          <Link 
                            href={member.socialLinks.facebook}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="team-member-card__social-link"
                            aria-label={`${member.name} Facebook profile`}
                          >
                            <Icon name="facebook" />
                          </Link>
                        )}
                        {member.socialLinks.instagram && (
                          <Link 
                            href={member.socialLinks.instagram}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="team-member-card__social-link"
                            aria-label={`${member.name} Instagram profile`}
                          >
                            <Icon name="instagram" />
                          </Link>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}