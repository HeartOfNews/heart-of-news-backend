import { render, screen } from '@testing-library/react';
import ArticleCard from './ArticleCard';
import { mockArticles } from '@/lib/test/api-test-utils';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
    };
  },
}));

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt} />;
  },
}));

describe('ArticleCard', () => {
  it('renders article title and summary', () => {
    const article = mockArticles[0];
    render(<ArticleCard article={article} />);
    
    expect(screen.getByText(article.title)).toBeInTheDocument();
    expect(screen.getByText(article.summary)).toBeInTheDocument();
  });
  
  it('renders article source and date', () => {
    const article = mockArticles[0];
    render(<ArticleCard article={article} />);
    
    expect(screen.getByText(article.source.name)).toBeInTheDocument();
    
    // Format date for comparison
    const formattedDate = new Date(article.published_at).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    expect(screen.getByText(new RegExp(formattedDate.replace(/\s+/g, '\\s+')))).toBeInTheDocument();
  });
  
  it('renders bias indicator when showBiasIndicator is true', () => {
    const article = mockArticles[0];
    render(<ArticleCard article={article} showBiasIndicator={true} />);
    
    // Check if bias indicator is present
    const biasScore = `Bias: ${(article.bias_score?.overall_score || 0) * 100}%`;
    expect(screen.getByText(new RegExp(biasScore))).toBeInTheDocument();
  });
  
  it('does not render bias indicator when showBiasIndicator is false', () => {
    const article = mockArticles[0];
    render(<ArticleCard article={article} showBiasIndicator={false} />);
    
    // Check that bias label is not present
    expect(screen.queryByText(/Left-leaning|Right-leaning|Neutral/)).not.toBeInTheDocument();
  });
  
  it('renders image when image_url is provided', () => {
    const article = mockArticles[0];
    render(<ArticleCard article={article} />);
    
    // Check if image is rendered
    const image = screen.getByRole('img');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', article.image_url);
  });
  
  it('renders fallback when image_url is not provided', () => {
    const articleWithoutImage = {
      ...mockArticles[0],
      image_url: undefined,
    };
    render(<ArticleCard article={articleWithoutImage} />);
    
    // Check if fallback is rendered
    expect(screen.getByText('No image available')).toBeInTheDocument();
  });
});