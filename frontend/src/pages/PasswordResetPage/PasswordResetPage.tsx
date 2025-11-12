import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Logo } from '@/components/common/Logo';
import { ROUTES } from '@/config/routes';
import { getErrorMessage } from '@/utils/errorHandler';
import type { ResetPasswordRequest } from '@/types/auth';

const resetPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
});

export const PasswordResetPage = () => {
  const { resetPassword } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordRequest>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const onSubmit = async (data: ResetPasswordRequest) => {
    setError(null);
    setSuccess(false);
    setIsLoading(true);

    try {
      await resetPassword(data);
      setSuccess(true);
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Failed to send reset email. Please try again.');
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="relative min-h-screen bg-background flex items-center justify-center px-4 py-12">
        <div className="pointer-events-none fixed inset-0 z-0">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5" />
          <div className="absolute inset-0 bg-grid-pattern opacity-30" />
          <div className="absolute left-0 top-1/4 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
          <div className="absolute bottom-1/4 right-0 h-96 w-96 rounded-full bg-secondary/10 blur-3xl" />
        </div>
        <div className="relative z-10 w-full max-w-md">
          <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl shadow-primary/10 border border-gray-200 p-6 md:p-8 text-center">
            <div className="text-4xl mb-4">✓</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Check Your Email
            </h1>
            <p className="text-gray-600 mb-6">
              We've sent a password reset link to your email address. Please check your inbox
              and follow the instructions.
            </p>
            <Link to={ROUTES.LOGIN}>
              <Button variant="primary" size="md" className="w-full">
                Back to Sign In
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-background flex items-center justify-center px-4 py-12">
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

        {/* Password Reset Form */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl shadow-primary/10 border border-gray-200 p-6 md:p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Reset Password
          </h1>

          <p className="text-gray-600 mb-6 text-center">
            Enter your email address and we'll send you a link to reset your password.
          </p>

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

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full"
              isLoading={isLoading}
            >
              Send Reset Link
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            Remember your password?{' '}
            <Link to={ROUTES.LOGIN} className="text-primary hover:underline font-medium">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

