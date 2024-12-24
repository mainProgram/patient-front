export interface IApiResponse {
  success: string;
  message: string;
  data: object|[]|null;
  errors: string[]|null;
  errorCode: number;
  timestamp: number;
}
