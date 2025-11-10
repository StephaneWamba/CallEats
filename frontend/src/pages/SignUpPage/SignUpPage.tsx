import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Logo } from '@/components/common/Logo';
import { ROUTES } from '@/config/routes';
import type { RegisterWithRestaurantRequest } from '@/types/auth';

const signUpSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  restaurant_name: z.string().min(1, 'Restaurant name is required'),
});

export const SignUpPage = () => {
  const navigate = useNavigate();
  const { registerWithRestaurant } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterWithRestaurantRequest>({
    resolver: zodResolver(signUpSchema),
    mode: 'onSubmit',
  });

  const onSubmit = async (data: RegisterWithRestaurantRequest) => {
    setError(null);
    setIsLoading(true);

    try {
      await registerWithRestaurant(data);
      navigate(ROUTES.DASHBOARD);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-background flex items-center justify-center px-4 py-12">
      {/* Background Pattern */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5" />
        <div className="absolute inset-0 bg-grid-pattern opacity-30" />
        <div className="absolute left-0 top-1/4 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-0 h-96 w-96 rounded-full bg-secondary/10 blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link to={ROUTES.LANDING}>
            <Logo size="md" showText={true} />
          </Link>
        </div>

        {/* Sign Up Form */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl shadow-primary/10 border border-gray-200 p-6 md:p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Create Your Restaurant Account
          </h1>

          {error && (
            <div className="mb-4 p-3 bg-error/10 border border-error rounded-lg text-error text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              placeholder="user@restaurant.com"
              error={errors.email?.message}
              {...register('email')}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              helperText="Must be at least 6 characters"
              {...register('password')}
            />

            <Input
              label="Restaurant Name"
              type="text"
              placeholder="My Restaurant"
              error={errors.restaurant_name?.message}
              {...register('restaurant_name')}
            />

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full"
              isLoading={isLoading}
            >
              Create Account
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to={ROUTES.LOGIN} className="text-primary hover:underline font-medium">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

