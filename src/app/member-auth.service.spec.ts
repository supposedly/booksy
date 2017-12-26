import { TestBed, inject } from '@angular/core/testing';

import { MemberAuthService } from './member-auth.service';

describe('MemberAuthService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MemberAuthService]
    });
  });

  it('should be created', inject([MemberAuthService], (service: MemberAuthService) => {
    expect(service).toBeTruthy();
  }));
});
