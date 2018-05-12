import { Pipe, PipeTransform } from '@angular/core';
/*
 * Titlecase but "people's books" --> "People's Books", not "People'S Books"
 */
@Pipe({name: 'titlespace'})
export class SpaceOnlyTitleCasePipe implements PipeTransform {
  transform(string: string): string {
    if (string == null) {
      return string;
    }
    return string.split(' ')
      .map(s => s[0].toUpperCase() + s.slice(1))
      .join(' ');
  }
}
